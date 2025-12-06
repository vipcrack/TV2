#!/usr/bin/env python3
"""
FFZYTV Android 项目自动构建器（CI 友好版）
- 使用本地 assets/gradle-wrapper.jar 避免网络依赖
- 生成完整 Android 项目
- 支持 ./gradlew assembleDebug
"""

import os
import sys

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

def get_local_gradle_wrapper_jar():
    jar_path = os.path.join("assets", "gradle-wrapper.jar")
    if not os.path.isfile(jar_path):
        print(f"[ERROR] Missing file: {jar_path}", file=sys.stderr)
        print("[INFO] Please run locally and commit:")
        print("  gradle wrapper --gradle-version 8.6")
        print("  mkdir -p assets && cp gradle/wrapper/gradle-wrapper.jar assets/")
        sys.exit(1)
    with open(jar_path, 'rb') as f:
        data = f.read()
    print(f"[INFO] Using local gradle-wrapper.jar ({len(data)} bytes)")
    return data

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
        print("[WARN] Pillow not installed, skipping icons (build still works)")
        return None

def main():
    print("[BUILD] Starting FFZYTV project generation...")
    
    root = PROJECT_NAME
    app_dir = os.path.join(root, "app")
    src = os.path.join(app_dir, "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")

    os.makedirs(java_root, exist_ok=True)
    for d in ["values", "layout", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # Config files
    write_file(os.path.join(root, "gradle.properties"), 
               "android.useAndroidX=true\norg.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n")

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

    write_file(os.path.join(root, "build.gradle"), 
               "plugins {\n    id 'com.android.application' version '8.3.0' apply false\n}\n")

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
    buildTypes {{
        release {{
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

    write_file(os.path.join(res, "values", "strings.xml"), 
               "<resources>\n    <string name=\"app_name\">FFZYTV</string>\n</resources>\n")

    write_file(os.path.join(res, "layout", "activity_main.xml"), """<?xml version="1.0" encoding="utf-8"?>
<TextView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:text="FFZYTV\\nhttps://cj.ffzyapi.com/"
    android:textColor="#FFFFFF"
    android:background="#2C3E50"/>
""")

    write_file(os.path.join(java_root, "MainActivity.java"), """package com.ffzy.tv;
import android.app.Activity;
import android.os.Bundle;
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }
}
""")

    # Icons (optional)
    ic_launcher = create_icon("FF", 192, (70, 130, 180), (255, 255, 255))
    banner = create_icon("FFZYTV", 320, (41, 128, 185), (255, 255, 255))
    if ic_launcher:
        ic_launcher.save(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"))
    if banner:
        banner.save(os.path.join(res, "drawable", "banner.png"))

    # Write Gradle Wrapper JAR
    print("[JAR] Writing gradle-wrapper.jar...")
    jar_data = get_local_gradle_wrapper_jar()
    write_binary_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.jar"), jar_data)

    write_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.properties"), """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.6-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    write_file(os.path.join(root, "gradlew"), """#!/bin/bash
APP_HOME="$(cd "$(dirname "$0")" && pwd)"
CLASSPATH="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"
exec java -Xmx64m -Xms64m -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
""")
    os.chmod(os.path.join(root, "gradlew"), 0o755)

    write_file(os.path.join(root, "gradlew.bat"), r"""@echo off
set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_HOME=%DIRNAME%
set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar
set JAVA_EXE=java
if exist "%JAVA_HOME%\bin\java.exe" set JAVA_EXE=%JAVA_HOME%\bin\java.exe
"%JAVA_EXE%" -Xmx64m -Xms64m -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
""")

    print(f"\n[SUCCESS] Project '{PROJECT_NAME}' generated!")
    print(f"[NEXT] Run: cd {PROJECT_NAME} && ./gradlew assembleDebug")
    print(f"[APK] Output: app/build/outputs/apk/debug/app-debug.apk")

if __name__ == "__main__":
    try:
        import subprocess
        subprocess.run(["java", "-version"], capture_output=True, check=True)
    except:
        print("[WARN] JDK 17+ is required for building APK")
    main()
