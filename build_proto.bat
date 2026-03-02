@echo off
CD /d %~dp0

echo - - - BUILD .PROTO - - -
protoc\protoc -I. --python_out=. protobufs\csgo.proto
echo - - - FINISHED - - -
pause