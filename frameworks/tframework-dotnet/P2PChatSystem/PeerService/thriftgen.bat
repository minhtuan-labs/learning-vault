@echo off
rmdir /s /q gen-netstd
D:\src\thrift\thrift-0.20.0.exe --gen netstd p2pchatsystem_datatypes.thrift
D:\src\thrift\thrift-0.20.0.exe --gen netstd bootstrapservice.thrift
D:\src\thrift\thrift-0.20.0.exe --gen netstd peerservice.thrift
