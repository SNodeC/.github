"""Exercise the workflow's own inline scripts, not a parallel implementation."""
from contextlib import contextmanager
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.load((ROOT / ".github/workflows/verify.yml").read_text(), Loader=yaml.BaseLoader)


def script(job, name):
    return next(s["run"] for s in WORKFLOW["jobs"][job]["steps"] if s.get("name") == name)


@contextmanager
def directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def prepare(path, ci):
    (path / ".snodec").mkdir(exist_ok=True)
    (path / ".snodec/repo.yml").write_text(yaml.safe_dump({"ci": ci}))
    output = path / "output"
    output.write_text("")
    with directory(path), patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}):
        exec(compile(script("prepare", "Read and validate manifest"), "manifest", "exec"), {})
    result = {}
    lines = iter(output.read_text().splitlines())
    for line in lines:
        if "<<" in line:
            key, delimiter = line.split("<<", 1)
            values = []
            for value in lines:
                if value == delimiter:
                    break
                values.append(value)
            result[key] = "\n".join(values)
        else:
            key, value = line.split("=", 1)
            result[key] = value
    return result


class ManifestTests(unittest.TestCase):
    def test_defaults_and_ipv6_capabilities(self):
        with tempfile.TemporaryDirectory() as directory_name:
            path = Path(directory_name)
            result = prepare(path, {})
            config = json.loads(result["config"])
            self.assertEqual(result["container"], "gcc:15.3.0-trixie")
            self.assertEqual(result["options"], "")
            self.assertEqual(config["ctest_args"], ["--output-on-failure"])
            self.assertTrue(config["ctest"])
            self.assertFalse(config["runtime_dirs"])
            self.assertEqual(config["timeout_minutes"], 60)
            result = prepare(path, {"ipv6": True, "container": "gcc:15.3.0-trixie"})
            self.assertEqual(result["options"],
                             "--cap-add=NET_ADMIN --sysctl net.ipv6.conf.all.disable_ipv6=0")

    def test_valid_custom_options(self):
        with tempfile.TemporaryDirectory() as directory_name:
            ci = {"profile": "cpp", "apt": ["libqt6core6-dev", "zlib1g-dev:amd64"],
                  "deps": ["snode.c@source", "AISuite@source"], "ctest": False,
                  "ctest_args": ["--output-on-failure", "-R", "test.*"],
                  "cmake_options": ["-DVALUE=with spaces;still one argument"]}
            result = prepare(Path(directory_name), ci)
            for key, value in ci.items():
                self.assertEqual(json.loads(result["config"])[key], value)

    def test_cpp_timeout_boundaries_and_python_profile_rejection(self):
        with tempfile.TemporaryDirectory() as name:
            for value in (10, 60, 180):
                with self.subTest(value=value):
                    config = json.loads(prepare(Path(name), {"timeout_minutes": value})["config"])
                    self.assertEqual(config["timeout_minutes"], value)
            ci = {"profile": "python", "native_build": ["python", "tools/build.py"],
                  "smoke": {system: ["program"] for system in ("Linux", "Windows", "macOS")},
                  "artifact_globs": ["dist/*.zip"], "timeout_minutes": 60}
            with self.assertRaises(ValueError):
                prepare(Path(name), ci)

    def test_invalid_manifests_fail_before_container(self):
        cases = [{"profile": "python"}, {"ipv6": "true"}, {"runtime_dirs": 1},
                 {"ctest": None}, {"apt": "--bad"}, {"deps": ["snode.c@release"]},
                 {"deps": ["snode.c@source"] * 2}, {"deps": ["snode.c@source", "snode.c@dev"]}, {"apt": ["--allow-unauthenticated"]},
                 {"apt": ["libssl-dev;echo bad"]}, {"container": "gcc:15\noptions=bad"},
                 {"cmake_options": [False]}, {"ctest_args": ["bad\0argument"]},
                 {"deps": ["other/snode.c@source"]}, {"unknown": 1}, {"parallel": 0}, {"parallel": True},
                 {"timeout_minutes": 9}, {"timeout_minutes": 181}, {"timeout_minutes": True},
                 {"timeout_minutes": "60"}, {"timeout_minutes": 60.0}, {"timeout_minutes": None},
                 {"sdk": "yes"}, {"env": {"GH_READ_TOKEN": "bad"}}, {"env": {"OK": 1}}]
        with tempfile.TemporaryDirectory() as directory_name:
            for ci in cases:
                with self.subTest(ci=ci), self.assertRaises(ValueError):
                    prepare(Path(directory_name), ci)
            path = Path(directory_name)
            for content in ("[]", "ci: false", "ci: []"):
                (path / ".snodec/repo.yml").write_text(content)
                with directory(path), self.assertRaises(ValueError):
                    exec(script("prepare", "Read and validate manifest"), {})
            (path / ".snodec/repo.yml").unlink()
            with directory(path), self.assertRaises(FileNotFoundError):
                exec(script("prepare", "Read and validate manifest"), {})


class WorkflowContractTests(unittest.TestCase):
    def test_triggers_and_exact_checkout(self):
        self.assertEqual(set(WORKFLOW["on"]), {"workflow_call"})
        self.assertEqual(WORKFLOW["jobs"]["cpp"]["name"], "snodec / cpp")
        self.assertEqual(WORKFLOW["permissions"], {"contents": "read"})
        for job in WORKFLOW["jobs"].values():
            checkout = next(s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout@"))
            self.assertEqual(checkout["with"]["ref"],
                             "${{ github.event.pull_request.head.sha || github.sha }}")
            self.assertEqual(checkout["with"]["persist-credentials"], "false")
        cpp = WORKFLOW["jobs"]["cpp"]
        self.assertEqual(cpp["container"]["image"], "${{ needs.prepare.outputs.container }}")
        self.assertEqual(cpp["container"]["options"], "${{ needs.prepare.outputs.options }}")

    def test_jobs_have_bounded_timeouts_fixed_linux_and_full_action_pins(self):
        jobs = WORKFLOW["jobs"]
        self.assertEqual(jobs["prepare"]["timeout-minutes"], "10")
        self.assertEqual(jobs["hygiene"]["timeout-minutes"], "15")
        self.assertEqual(jobs["python"]["timeout-minutes"], "60")
        self.assertEqual(jobs["cpp"]["timeout-minutes"],
                         "${{ fromJSON(needs.prepare.outputs.config).timeout_minutes }}")
        for name, job in jobs.items():
            self.assertEqual(job["runs-on"], "${{ matrix.os }}" if name == "python" else "ubuntu-24.04")
            for step in job["steps"]:
                if "uses" in step:
                    self.assertRegex(step["uses"], r"^actions/(checkout|setup-python|upload-artifact)@[0-9a-f]{40}$")
        text = (ROOT / ".github/workflows/verify.yml").read_text()
        for line in text.splitlines():
            if "uses:" in line:
                self.assertRegex(line, r"@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$")

    def test_documentation_has_one_authority_at_called_workflow_sha(self):
        steps = WORKFLOW["jobs"]["hygiene"]["steps"]
        checkout = next(step for step in steps if step.get("name") == "Check out the called workflow tooling")
        self.assertEqual(checkout["with"]["repository"], "${{ job.workflow_repository }}")
        self.assertEqual(checkout["with"]["ref"], "${{ job.workflow_sha }}")
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        self.assertEqual(checkout["with"]["path"], ".snodec-ci-tools")
        for name in ("Check whitespace against PR base or previous commit", "Check changed source formatting"):
            check = next(step for step in steps if step.get("name") == name)
            self.assertLess(steps.index(checkout), steps.index(check))
            self.assertEqual(check["if"], "${{ always() && !cancelled() }}")
        audit = next(step for step in steps if step.get("name") == "Audit all tracked documentation")
        self.assertEqual(audit["if"], "${{ always() && !cancelled() }}")
        self.assertIn('docs-audit --repo "$GITHUB_WORKSPACE"', audit["run"])
        self.assertNotIn('path.suffix.lower() == ".md"', script("hygiene", "Check changed source formatting"))
        self.assertIn("python3-yaml", next(step["run"] for step in steps if "apt-get install" in step.get("run", "")))
        self.assertNotIn("secrets.", (ROOT / ".github/workflows/verify.yml").read_text())

    def test_template_exact_and_control_checks_independent(self):
        self.assertEqual((ROOT / "templates/ci.yml").read_text(),
                         "name: CI\non: [workflow_dispatch]\n"
                         "permissions: { contents: read }\njobs:\n  snodec:\n"
                         "    uses: SNodeC/.github/.github/workflows/verify.yml@v1.0\n"
                         "    secrets: inherit\n")
        ci = yaml.load((ROOT / ".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader)
        steps = ci["jobs"]["control"]["steps"]
        for name in ("Unit and workflow boundary tests", "Check generated profile drift"):
            step = next(s for s in steps if s.get("name") == name)
            self.assertEqual(step["if"], "${{ always() && !cancelled() }}")
        manifest = yaml.safe_load((ROOT / "templates/repo.yml").read_text())
        with tempfile.TemporaryDirectory() as directory_name:
            self.assertEqual(json.loads(prepare(Path(directory_name), manifest["ci"])["config"]),
                             manifest["ci"])

    def test_base_packages(self):
        step = script("cpp", "Install base build packages")
        for package in ("cmake", "ninja-build", "pkg-config", "git", "ca-certificates",
                        "libssl-dev", "libmagic-dev", "libbluetooth-dev",
                        "nlohmann-json3-dev", "iproute2"):
            self.assertIn(package, step)
        self.assertIn("gcc --version", script("cpp", "Record toolchain versions"))

    def test_runtime_and_ipv6_are_opt_in(self):
        code = script("cpp", "Install extra packages and prepare runtime")
        with patch("subprocess.run") as run, patch.dict(os.environ, {"CI_CONFIG": json.dumps(
            {"apt": [], "runtime_dirs": False, "ipv6": False})}):
            exec(code, {})
            commands = [call.args[0] for call in run.call_args_list]
            self.assertTrue(any(c[0] == "useradd" for c in commands))
            self.assertFalse(any(c[0] in ("ip", "install", "apt-get") for c in commands))
        with patch("subprocess.run") as run, patch("grp.getgrnam", side_effect=KeyError), \
                patch.dict(os.environ, {"CI_CONFIG": json.dumps(
                    {"apt": ["zlib1g-dev"], "runtime_dirs": True, "ipv6": True})}):
            exec(code, {})
            commands = [c.args[0] for c in run.call_args_list]
            self.assertIn(["groupadd", "--system", "snodec"], commands)
            self.assertIn(["install", "-d", "-m", "0770", "-g", "snodec",
                           "/etc/snode.c", "/var/log/snode.c", "/var/run/snode.c"], commands)
            self.assertIn(["ip", "-6", "address", "add", "fd00::1/128", "dev", "snodec-ci-v6"], commands)

    def test_disabled_ctest_and_arguments_are_not_shell_code(self):
        with tempfile.TemporaryDirectory() as directory_name:
            ci = json.loads(prepare(Path(directory_name), {"ctest": False,
                            "cmake_options": ["-DTEXT=a value;echo not executed"]})["config"])
            with patch("subprocess.run") as run, patch("subprocess.check_output", return_value="a" * 40), patch.dict(os.environ, {
                "CI_CONFIG": json.dumps(ci), "GITHUB_WORKSPACE": directory_name,
                "RUNNER_TEMP": directory_name, "GH_READ_TOKEN": "must-not-leak",
                "GITHUB_REPOSITORY": "SNodeC/fixture",
            }):
                exec(script("cpp", "Build ordered source dependencies, test and stage caller"), {})
                commands = [call.args[0] for call in run.call_args_list]
                self.assertFalse(any(c[0] == "ctest" for c in commands))
                self.assertIn("-DTEXT=a value;echo not executed", commands[0])
                for call in run.call_args_list:
                    self.assertNotIn("GH_READ_TOKEN", call.kwargs["env"])
                    self.assertNotIn("shell", call.kwargs)


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def commit(path):
    git(path, "add", ".")
    git(path, "-c", "user.name=Test fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-m", "Fixture")


def dependency(path, name, first=False):
    path.mkdir()
    git(path, "init", "--initial-branch=dependency/from-api")
    (path / f"{name}.h").write_text(f"int {name}();\n")
    code = f"int {name}() {{ return 41; }}\n" if first else (
        '#include "depone.h"\nint deptwo() { return depone() + 1; }\n')
    (path / f"{name}.cpp").write_text(code)
    cmake = f"""cmake_minimum_required(VERSION 3.20)
project({name} LANGUAGES CXX)
add_library({name} STATIC {name}.cpp)
target_include_directories({name} PUBLIC $<BUILD_INTERFACE:${{CMAKE_CURRENT_SOURCE_DIR}}> $<INSTALL_INTERFACE:include>)
install(TARGETS {name} EXPORT {name}Targets ARCHIVE DESTINATION lib)
install(FILES {name}.h DESTINATION include)
install(EXPORT {name}Targets FILE {name}Config.cmake NAMESPACE {name}:: DESTINATION lib/cmake/{name})
"""
    if not first:
        cmake += "find_package(depone CONFIG REQUIRED)\ntarget_link_libraries(deptwo PUBLIC depone::depone)\n"
    (path / "CMakeLists.txt").write_text(cmake)
    commit(path)
    return git(path, "rev-parse", "HEAD")


class BuildBoundaryTests(unittest.TestCase):
    def test_real_ordered_dependency_consumer_ctest_and_install(self):
        with tempfile.TemporaryDirectory() as directory_name:
            root = Path(directory_name)
            commits = {name: dependency(root / name, name, first=name == "depone")
                       for name in ("depone", "deptwo")}
            caller = root / "caller"
            caller.mkdir()
            (caller / "main.cpp").write_text('#include "deptwo.h"\nint main() { return deptwo() == 42 ? 0 : 1; }\n')
            (caller / "CMakeLists.txt").write_text("""cmake_minimum_required(VERSION 3.20)
project(consumer LANGUAGES CXX)
find_package(depone CONFIG REQUIRED)
find_package(deptwo CONFIG REQUIRED)
add_executable(consumer main.cpp)
target_link_libraries(consumer PRIVATE deptwo::deptwo)
enable_testing()
add_test(NAME first_success COMMAND consumer)
install(TARGETS consumer DESTINATION bin)
""")
            git(caller, "init", "--initial-branch=caller/default")
            commit(caller)
            ci = json.loads(prepare(caller, {"deps": ["depone@source", "deptwo@source"],
                "env": {"TIMING_POLICY": "report"}, "ctest_launcher": ["env", "BOUNDARY_LAUNCHER=active"]})["config"])
            requests, commands = [], []
            actual_run = subprocess.run

            def response(request, **kwargs):
                url = request.full_url
                requests.append(url)
                self.assertEqual(request.get_header("Authorization"), "Bearer read-only-fixture")
                name = url.split("/")[5]
                data = {"sha": commits[name]} if "/commits/" in url else {"default_branch": "dependency/from-api"}
                return io.BytesIO(json.dumps(data).encode())

            def run(args, **kwargs):
                commands.append((list(args), dict(kwargs.get("env", os.environ))))
                self.assertNotIn("GH_READ_TOKEN", kwargs.get("env", os.environ))
                self.assertEqual(kwargs["env"]["TIMING_POLICY"], "report")
                if args[0] == "git" and "remote" in args:
                    args[-1] = str(root / Path(args[2]).name)
                if args[0] == "chown":
                    return subprocess.CompletedProcess(args, 0)
                if args[0] == "runuser":
                    args = args[args.index("--") + 1:]
                return actual_run(args, **kwargs)

            with patch.dict(os.environ, {"CI_CONFIG": json.dumps(ci),
                                         "GITHUB_WORKSPACE": str(caller), "RUNNER_TEMP": str(root),
                                         "GH_READ_TOKEN": "read-only-fixture", "GITHUB_REPOSITORY": "SNodeC/consumer"}), \
                    patch("urllib.request.urlopen", side_effect=response), \
                    patch("subprocess.run", side_effect=run):
                exec(script("cpp", "Build ordered source dependencies, test and stage caller"), {})
            stage = root / "snodec/stage/caller/bin/consumer"
            self.assertTrue(stage.is_file())
            self.assertEqual(subprocess.run([stage]).returncode, 0)
            self.assertEqual(requests, [
                f"https://api.github.com/repos/SNodeC/{name}" + suffix
                for name in ("depone", "deptwo")
                for suffix in ("", "/commits/dependency%2Ffrom-api")
            ])
            fetches = [cmd[-1] for cmd, _ in commands if cmd[0] == "git" and "fetch" in cmd]
            self.assertEqual(fetches, list(commits.values()))
            configurations = [(cmd, env) for cmd, env in commands if cmd[:2] == ["cmake", "-S"]]
            self.assertEqual([Path(cmd[2]).name for cmd, _ in configurations], ["depone", "deptwo", "caller"])
            self.assertIn(str(root / "snodec/stage/depone/lib"), configurations[1][1]["LD_LIBRARY_PATH"])
            self.assertIn(str(root / "snodec/stage/deptwo/lib"), configurations[2][1]["LD_LIBRARY_PATH"])
            tests = [cmd for cmd, _ in commands if "ctest" in cmd]
            self.assertEqual(len(tests), 1)
            self.assertIn("--output-on-failure", tests[0])
            self.assertIn("BOUNDARY_LAUNCHER=active", tests[0])
            self.assertFalse((root / "snodec/stage/caller/.snodec-sdk.json").exists())

    def test_whitespace_initial_push_and_pr_base(self):
        code = script("hygiene", "Check whitespace against PR base or previous commit")
        with tempfile.TemporaryDirectory() as directory_name:
            path = Path(directory_name)
            git(path, "init", "--initial-branch=fixture/default")
            (path / "file").write_text("clean\n")
            commit(path)
            initial = git(path, "rev-parse", "HEAD")
            def check(base=""):
                result = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", code], cwd=path,
                                        env=os.environ | {"PR_BASE": base}, capture_output=True)
                return result.returncode
            self.assertEqual(check(), 0)
            (path / "file").write_text("bad trailing whitespace  \n")
            commit(path)
            self.assertNotEqual(check(), 0)
            (path / "other").write_text("clean\n")
            commit(path)
            self.assertEqual(check(), 0)
            self.assertNotEqual(check(initial), 0)


class PhaseTwoBoundaryTests(unittest.TestCase):
    def test_python_manifest_and_native_commands(self):
        ci = {"profile": "python", "native_build": ["python", "tools/build.py"],
              "smoke": {system: ["dist/program", "--smoke-test"] for system in ("Linux", "Windows", "macOS")},
              "artifact_globs": ["dist/*.zip", "dist/*.tar.gz"]}
        with tempfile.TemporaryDirectory() as name:
            output = prepare(Path(name), ci)
            config = json.loads(output["config"])
            self.assertEqual(output["profile"], "python")
            self.assertEqual(output["artifact_paths"], "dist/*.zip\ndist/*.tar.gz")
            with patch("subprocess.run") as run, patch.dict(os.environ, {
                "CI_CONFIG": output["config"], "RUNNER_OS": "Windows",
            }):
                exec(script("python", "Install development dependencies"), {})
                exec(script("python", "Build native package"), {})
                exec(script("python", "Native packaged launch"), {})
            self.assertEqual([call.args[0] for call in run.call_args_list], [
                ["python", "-m", "pip", "install", "-e", ".[dev]"],
                ci["native_build"], ci["smoke"]["Windows"],
            ])
            self.assertEqual(config["python_version"], "3.12")
            for change in ({"smoke": {}}, {"python_version": "2.7"}, {"pip": "remote-package"},
                           {"native_build": "python build.py"}, {"artifact_globs": ["bad\npath"]}):
                with self.subTest(change=change), self.assertRaises(ValueError):
                    prepare(Path(name), ci | change)
        job = WORKFLOW["jobs"]["python"]
        self.assertEqual(job["strategy"]["matrix"]["os"], ["ubuntu-24.04", "windows-2025", "macos-15"])
        self.assertEqual(job["strategy"]["fail-fast"], "false")
        self.assertIn('not audio_device', script("python", "Tests independent of physical audio devices"))

    def test_changed_file_hygiene_collects_all_failures(self):
        code = script("hygiene", "Check changed source formatting")
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            git(root, "init", "--initial-branch=hygiene/from-api")
            (root / "old.md").write_text("[legacy](missing-old.md)\n")
            commit(root)
            (root / ".clang-format").write_text("BasedOnStyle: LLVM\n")
            (root / ".cmake-format.py").write_text("")
            (root / "changed.cpp").write_text("int main() {return 0;}\n")
            (root / "CMakeLists.txt").write_text("project( test)\n")
            (root / "new.md").write_text("[external](https://example.invalid) [missing](missing-new.md)\n```\n[code](ignored.md)\n```\n")
            commit(root)
            actual_run = subprocess.run
            tools = []

            def run(args, **kwargs):
                if args[0] in ("clang-format", "cmake-format"):
                    tools.append(args[0])
                    return subprocess.CompletedProcess(args, 1)
                return actual_run(args, **kwargs)

            with directory(root), patch.dict(os.environ, {"PR_BASE": ""}), patch("subprocess.run", side_effect=run):
                with self.assertRaises(SystemExit) as error:
                    exec(code, {})
            self.assertEqual(set(tools), {"clang-format", "cmake-format"})
            self.assertIn("changed.cpp: clang-format", str(error.exception))
            self.assertIn("CMakeLists.txt: cmake-format", str(error.exception))
            self.assertNotIn("missing-new.md", str(error.exception))

    def test_workflow_docs_audit_checks_old_and_new_tracked_pages(self):
        code = script("hygiene", "Audit all tracked documentation")
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            git(root, "init", "--initial-branch=audit/from-api")
            git(root, "remote", "add", "origin", "https://github.com/SNodeC/AutoTalk.git")
            (root / "README.md").write_text("[old](old.md)\n")
            (root / "old.md").write_text("[old missing](missing-old.md)\n")
            commit(root)
            (root / "README.md").write_text("[old](old.md) [new](new.md)\n")
            (root / "new.md").write_text("[new missing](missing-new.md)\n```\n[code](ignored.md)\n```\n")
            commit(root)
            (root / ".snodec-ci-tools").symlink_to(ROOT, target_is_directory=True)
            result = subprocess.run(["bash", "-e", "-c", code], cwd=root,
                                    env=os.environ | {"GITHUB_WORKSPACE": str(root)}, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing-old.md", result.stdout)
            self.assertIn("missing-new.md", result.stdout)
            self.assertNotIn("ignored.md", result.stdout)
            (root / "missing-old.md").write_text("Old target\n")
            (root / "missing-new.md").write_text("New target\n")
            git(root, "add", ".")
            result = subprocess.run(["bash", "-e", "-c", code], cwd=root,
                                    env=os.environ | {"GITHUB_WORKSPACE": str(root)}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("0 violations", result.stdout)

    def test_source_only_verification_has_no_publication_capability(self):
        self.assertFalse((ROOT / ".github/workflows/publish-dev.yml").exists())
        self.assertEqual(WORKFLOW["permissions"], {"contents": "read"})
        cpp = WORKFLOW["jobs"]["cpp"]
        self.assertNotIn("outputs", cpp)
        self.assertNotIn("strategy", cpp)
        self.assertFalse(any("upload-artifact" in step.get("uses", "") for step in cpp["steps"]))
        code = script("cpp", "Build ordered source dependencies, test and stage caller")
        for removed in ("releases/", "tarfile", "platform", ".snodec-sdk.json", "@dev"):
            self.assertNotIn(removed, code)
        with tempfile.TemporaryDirectory() as name:
            for unsupported in ({"sdk": True}, {"sdk": False}, {"deps": ["snode.c@dev"]}):
                with self.subTest(unsupported=unsupported), self.assertRaises(ValueError):
                    prepare(Path(name), unsupported)
