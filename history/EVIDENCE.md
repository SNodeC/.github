# Evidence and pending confirmation

The catalog classification, lifecycle and supplied identity wording follow the
Phase 1 task. No repository was reclassified from GitHub's `fork` flag: course
projects remain community snapshots; only the six designated upstream forks use
the fork kind. Their `upstream` values come from the GitHub API `parent.full_name`.

The checked-in [metadata snapshot](../profile/github-metadata.json) records source
commits and default branches from `GET /repos/SNodeC/{name}` and
`GET /repos/SNodeC/{name}/commits/{default_branch}`. Existing workflow paths
were cross-checked against each commit's recursive Git tree and
`GET /repos/SNodeC/{name}/actions/workflows`. Release tags come from
`GET /repos/SNodeC/{name}/releases`: newest listed non-draft stable release,
or newest listed non-draft pre-release when no stable release exists.
These are review-time facts, not live claims. The new control CI is delivered
in this change, so its workflow path is included without a source-commit claim.

## Summaries awaiting maintainer confirmation

All rows below retain `confirm: true` even where source supports the wording.
Source links use exact verified commit SHAs, never an assumed branch name.

| Repository | Source evidence |
| --- | --- |
| GpsdOsmViewer | [app/src/main/java/at/vchrist/gpsdosmviewer/MainActivity.kt](https://github.com/SNodeC/GpsdOsmViewer/blob/d15df4a185160856823f65746a1f9ee1584b3435/app/src/main/java/at/vchrist/gpsdosmviewer/MainActivity.kt) |
| echo | [EchoServer.cpp](https://github.com/SNodeC/echo/blob/b8be500441c387c6cb834d584b7810b17d59bcec/EchoServer.cpp) · [EchoClient.cpp](https://github.com/SNodeC/echo/blob/b8be500441c387c6cb834d584b7810b17d59bcec/EchoClient.cpp) |
| websocket-echo | [echoserver.cpp](https://github.com/SNodeC/websocket-echo/blob/c8ee1f6f792e195e1aa95a1ebe12ecde084067e5/echoserver.cpp) · [subprotocol/server/echo/Echo.cpp](https://github.com/SNodeC/websocket-echo/blob/c8ee1f6f792e195e1aa95a1ebe12ecde084067e5/subprotocol/server/echo/Echo.cpp) |
| tiktaktoe | [tiktaktoe.cpp](https://github.com/SNodeC/tiktaktoe/blob/5c61f6bfc8a74b450f2fb4e83a3e4521a6a08b3c/tiktaktoe.cpp) · [TikTakToeGameModel.cpp](https://github.com/SNodeC/tiktaktoe/blob/5c61f6bfc8a74b450f2fb4e83a3e4521a6a08b3c/TikTakToeGameModel.cpp) |
| ServerClient | [ChatApp.cpp](https://github.com/SNodeC/ServerClient/blob/d063975460cd6d0f1f522a87f7ac3748c4aa131c/ChatApp.cpp) · [client.cpp](https://github.com/SNodeC/ServerClient/blob/d063975460cd6d0f1f522a87f7ac3748c4aa131c/client.cpp) · [server.cpp](https://github.com/SNodeC/ServerClient/blob/d063975460cd6d0f1f522a87f7ac3748c4aa131c/server.cpp) |
| MiniGateway | [main.cpp](https://github.com/SNodeC/MiniGateway/blob/2647f13bd9ee0dffdd4947818dbff50c40d73014/main.cpp) · [MiniGatewayMqtt.cpp](https://github.com/SNodeC/MiniGateway/blob/2647f13bd9ee0dffdd4947818dbff50c40d73014/MiniGatewayMqtt.cpp) |
| INJA-Templatebuilder | [backend/src/main.cpp](https://github.com/SNodeC/INJA-Templatebuilder/blob/c770eafb4e852981888efc8f6fafb922530dda60/backend/src/main.cpp) |
| IM510-Project | [IM510-Project/ForumController.cpp](https://github.com/SNodeC/IM510-Project/blob/0bd5f6f0e831cc7f9cb53ec7e9879cb87c058ec0/IM510-Project/ForumController.cpp) |
| snodec-forum-webapp | [main.cpp](https://github.com/SNodeC/snodec-forum-webapp/blob/20fba09d2b66a57a98a9b3812bd6c89f5d439ef0/main.cpp) · [public/routes.js](https://github.com/SNodeC/snodec-forum-webapp/blob/20fba09d2b66a57a98a9b3812bd6c89f5d439ef0/public/routes.js) |
| SnodeCWebForum | [src/main.cpp](https://github.com/SNodeC/SnodeCWebForum/blob/ebf5a4595f7313f3c82f35d221f40a1260e677db/src/main.cpp) |
| simple-form-snodec | [rest-server/src/rest_server.cpp](https://github.com/SNodeC/simple-form-snodec/blob/157c860bc91ab678658a9f8ca37f69e866bffefd/rest-server/src/rest_server.cpp) · [rest-server/src/api_router.cpp](https://github.com/SNodeC/simple-form-snodec/blob/157c860bc91ab678658a9f8ca37f69e866bffefd/rest-server/src/api_router.cpp) |
| IOTApplicationDesigner | [src/components/Sidebar.tsx](https://github.com/SNodeC/IOTApplicationDesigner/blob/c89caddefbed1391581f68bfb00fb369a8882031/src/components/Sidebar.tsx) · [backend/src/my-express-server/classes/export/ExportHandler.mjs](https://github.com/SNodeC/IOTApplicationDesigner/blob/c89caddefbed1391581f68bfb00fb369a8882031/backend/src/my-express-server/classes/export/ExportHandler.mjs) |
| leiches-masterproject | [backend/src/http_ws_server.cpp](https://github.com/SNodeC/leiches-masterproject/blob/167e3b7de85b192ffc698777af02ea5df1ae467a/backend/src/http_ws_server.cpp) · [backend/src/hue_client.cpp](https://github.com/SNodeC/leiches-masterproject/blob/167e3b7de85b192ffc698777af02ea5df1ae467a/backend/src/hue_client.cpp) |
| mqtt-open-hue | [src/main.cpp](https://github.com/SNodeC/mqtt-open-hue/blob/b4ee0bc58e893fcbc532697b24aaa2bc15c1145e/src/main.cpp) |

## Mark and maintainer

The mark is copied byte-for-byte from [snode.c/docs/readme/media/snodec-mark.svg](https://github.com/SNodeC/snode.c/blob/c17b9aee773efa763f0fe092e626b07e76350b8b/docs/readme/media/snodec-mark.svg).
Maintainer identity is present in [SNode.C source headers](https://github.com/SNodeC/snode.c/blob/c17b9aee773efa763f0fe092e626b07e76350b8b/CMakeLists.txt)
and confirmed by [the GitHub user API](https://api.github.com/users/VolkerChristian).
The security contact is the existing email field of
[the organization API](https://api.github.com/orgs/SNodeC); no address was guessed.

The default GCC image manifest was verified in the official Docker registry:
`gcc:15.3.0-trixie`, index digest
`sha256:1fdcd041afad61e21d4ca0f8046e36f8da61baaa815f5ba290e39a15c487926a`.
The tag remains configurable; this digest is evidence, not a second image setting.
