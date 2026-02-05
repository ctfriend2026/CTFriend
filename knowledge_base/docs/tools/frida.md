# Frida 

[Frida Examples](https://book.hacktricks.xyz/mobile-pentesting/android-app-pentesting/frida-tutorial)

## Crypto Tracer Example
```javascript
setImmediate(function () {
    console.log("[ * ] Starting Post Data Trace");
    Java.perform(function() {
        let AESUtil = Java.use("com.thingclips.smart.android.common.utils.AESUtil");
        AESUtil["setALGO"].implementation = function (str) {
            console.log(`AESUtil.setALGO is called: str=${str}`);
            this["setALGO"](str);
        };
        AESUtil["setKeyValue"].implementation = function (bArr) {
            console.log(`AESUtil.setKeyValue is called: bArr=${bArr}`);
            this["setKeyValue"](bArr);
        };

        AESUtil["generateKey"].implementation = function () {
            console.log(`AESUtil.generateKey is called`);
            let result = this["generateKey"]();
            console.log(`AESUtil.generateKey result=${result.getAlgorithm()}`);
            return result;
        };
        AESUtil["generateKey"].implementation = function (str) {
            console.log("[*] Call stack:");
            console.log(Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));

            this["generateKey"]();
        };
        console.log("Performing hook");
    });
});
```