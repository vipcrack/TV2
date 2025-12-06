#!/usr/bin/env python3
import os
import subprocess
import sys
import base64
import urllib.request
import zipfile
import io

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def write_binary_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)

def create_icon(text, size, bg, fg):
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (size, size), bg)
        draw = ImageDraw.Draw(img)
        draw.text((size // 2, size // 2), text, fill=fg, anchor="mm")
        return img
    except ImportError:
        print("⚠️ Pillow not installed. Skipping icon generation.")
        return None

def download_and_extract_gradle_wrapper():
    print("📥 下载 gradle-8.6-bin.zip 并提取 gradle-wrapper.jar...")
    url = "https://services.gradle.org/distributions/gradle-8.6-bin.zip"
    try:
        with urllib.request.urlopen(url) as resp:
            data = resp.read()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            jar_data = zf.read("gradle-8.6/gradle/wrapper/gradle-wrapper.jar")
        return jar_data
    except Exception as e:
        print(f"❌ 下载失败: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    root = PROJECT_NAME
    app_dir = os.path.join(root, "app")
    src = os.path.join(app_dir, "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")
    keystore_path = os.path.join(app_dir, "ffzytv.keystore")

    os.makedirs(java_root, exist_ok=True)
    for d in ["values", "layout", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # gradle.properties
    write_file(os.path.join(root, "gradle.properties"), "android.useAndroidX=true\norg.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n")

    # settings.gradle
    write_file(os.path.join(root, "settings.gradle"), f"""pluginManagement {{
    repositories {{
        gradlePluginPortal()
        google()
        mavenCentral()
    }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}
rootProject.name = '{PROJECT_NAME}'
include ':app'
""")

    # root build.gradle
    write_file(os.path.join(root, "build.gradle"), "plugins {\n    id 'com.android.application' version '8.3.0' apply false\n}\n")

    # app build.gradle
    write_file(os.path.join(app_dir, "build.gradle"), f"""plugins {{
    id 'com.android.application'
}}

android {{
    namespace '{PACKAGE_NAME}'
    compileSdk 34
    defaultConfig {{
        applicationId "{PACKAGE_NAME}"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }}
    signingConfigs {{
        release {{
            storeFile file("ffzytv.keystore")
            storePassword "mypassword"
            keyAlias "ffzytv"
            keyPassword "mypassword"
        }}
    }}
    buildTypes {{
        release {{
            signingConfig signingConfigs.release
            minifyEnabled false
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.12.0'
}}
""")

    # AndroidManifest.xml
    write_file(os.path.join(src, "AndroidManifest.xml"), f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:banner="@drawable/banner">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LEANBACK_LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

    # strings.xml
    write_file(os.path.join(res, "values", "strings.xml"), "<resources>\n    <string name=\"app_name\">FFZYTV</string>\n</resources>\n")

    # activity_main.xml
    write_file(os.path.join(res, "layout", "activity_main.xml"), """<?xml version="1.0" encoding="utf-8"?>
<TextView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:text="FFZYTV\\nhttps://cj.ffzyapi.com/"
    android:textColor="#FFFFFF"
    android:background="#2C3E50"/>
""")

    # MainActivity.java
    write_file(os.path.join(java_root, "MainActivity.java"), """package com.ffzy.tv;
import android.app.Activity;
import android.os.Bundle;
public class MainActivity extends Activity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }}
}}
""")

    # Icons
    ic_launcher = create_icon("FF", 192, (70, 130, 180), (255, 255, 255))
    banner = create_icon("FFZYTV", 320, (41, 128, 185), (255, 255, 255))
    if ic_launcher:
        ic_launcher.save(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"))
    if banner:
        banner.save(os.path.join(res, "drawable", "banner.png"))

    # gradle-wrapper.jar
    jar_data = download_and_extract_gradle_wrapper()
    write_binary_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.jar"), jar_data)

    # gradle-wrapper.properties
    write_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.properties"), """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.6-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # gradlew (Linux/macOS)
    GRADLEW_CONTENT = """#!/bin/bash
PRG="$0"
while [ -h "$PRG" ] ; do
  ls=`ls -ld "$PRG"`
  link=`expr "$ls" : '.*-> \\(.*\\)$'`
  if expr "$link" : '/.*' > /dev/null; then
    PRG="$link"
  else
    PRG=`dirname "$PRG"`"/$link"
  fi
done
SAVED="`pwd`"
cd "`dirname \\"$PRG\\"`/" >/dev/null
APP_HOME="`pwd -P`"
cd "$SAVED" >/dev/null

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar

if [ -n "$JAVA_HOME" ] ; then
  JAVACMD="$JAVA_HOME/bin/java"
else
  JAVACMD="java"
fi

exec "$JAVACMD" -Xmx64m -Xms64m \\
  -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
"""
    write_file(os.path.join(root, "gradlew"), GRADLEW_CONTENT)
    os.chmod(os.path.join(root, "gradlew"), 0o755)

    # gradlew.bat (Windows)
    GRADLEW_BAT = r"""@echo off
set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_HOME=%DIRNAME%

set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar

@if "%JAVA_HOME%" == "" goto noJavaHome
set JAVA_EXE=%JAVA_HOME%/bin/java.exe
if exist "%JAVA_EXE%" goto execute
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
exit /b 1

:noJavaHome
set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% neq 0 (
  echo ERROR: JAVA_HOME is not set and no 'java' command could be found.
  exit /b 1
)

:execute
"%JAVA_EXE%" -Xmx64m -Xms64m -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
"""
    write_file(os.path.join(root, "gradlew.bat"), GRADLEW_BAT)

    # Try to generate keystore, but skip on failure
    keystore_ok = False
    if not os.path.exists(keystore_path):
        print("🔑 尝试生成签名密钥...")
        try:
            result = subprocess.run([
                "keytool", "-genkeypair",
                "-v", "-storetype", "PKCS12",
                "-keystore", keystore_path,
                "-alias", "ffzytv",
                "-keyalg", "RSA", "-keysize", "2048",
                "-validity", "10000",
                "-dname", "CN=FFZYTV, OU=TV, O=FFZY, C=CN",
                "-storepass", "mypassword",
                "-keypass", "mypassword"
            ], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                keystore_ok = True
                print("✅ 签名密钥生成成功")
            else:
                print("⚠️ keytool 失败，将使用调试签名")
        except Exception as e:
            print(f"⚠️ keytool 不可用: {e}，将使用调试签名")

    print(f"\n✅ 项目 '{PROJECT_NAME}' 已生成！")
    if keystore_ok:
        print(f"📦 构建正式版: cd {PROJECT_NAME} && ./gradlew assembleRelease")
    else:
        print(f"🧪 构建调试版: cd {PROJECT_NAME} && ./gradlew assembleDebug")
        print("   (正式签名密钥未生成，APK 将使用调试签名)")

if __name__ == "__main__":
    main()
