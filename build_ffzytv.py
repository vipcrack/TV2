#!/usr/bin/env python3
"""
FFZYTV Android 项目自动构建器（CI 友好版）
- 使用本地 assets/gradle-wrapper.jar 避免网络依赖
- 生成完整 Android 项目
- 支持 ./gradlew assembleDebug
"""

import os
import sys
import tempfile
import base64

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

def get_local_gradle_wrapper_jar():
    """从本地 assets/ 读取 gradle-wrapper.jar"""
    jar_path = os.path.join("assets", "gradle-wrapper.jar")
    if not os.path.isfile(jar_path):
        print(f"[ERROR] 找不到 {jar_path}", file=sys.stderr)
        print("[INFO] 解决方案:")
        print("   1. 在本地运行以下命令生成 JAR:")
        print("        gradle wrapper --gradle-version 8.6")
        print("        mkdir -p assets && cp gradle/wrapper/gradle-wrapper.jar assets/")
        print("   2. 提交到 Git:")
        print("        git add assets/gradle-wrapper.jar")
        print("        git commit -m 'Add gradle-wrapper.jar'")
        print("        git push")
        sys.exit(1)
    with open(jar_path, 'rb') as f:
        data = f.read()
    print(f"[INFO] 使用本地 gradle-wrapper.jar ({len(data)} 字节)")
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
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (size, size), bg)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.load_default()
            draw.text((size // 2, size // 2), text, fill=fg, anchor="mm", font=font)
        except:
            draw.text((size // 2, size // 2), text, fill=fg, anchor="mm")
        return img
    except ImportError:
        print("[WARN] 未安装 Pillow，跳过图标生成（不影响构建）")
        return None

def main():
    print("[BUILD] FFZYTV 构建器启动 (使用预提交的 gradle-wrapper.jar)")
    
    root = PROJECT_NAME
    app_dir = os.path.join(root, "app")
    src = os.path.join(app_dir, "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")

    print("[BUILD] 正在生成项目结构...")
    os.makedirs(java_root, exist_ok=True)
    for d in ["values", "layout", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # === 配置文件 ===
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

    # === 图标（可选）===
    ic_launcher = create_icon("FF", 192, (70, 130, 180), (255, 255, 255))
    banner = create_icon("FFZYTV", 320, (41, 128, 185), (255, 255, 255))
    if ic_launcher:
        ic_launcher.save(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"))
    if banner:
        banner.save(os.path.join(res, "drawable", "banner.png"))

    # === 关键：使用本地 gradle-wrapper.jar ===
    print("[JAR] 写入 Gradle Wrapper JAR...")
    jar_data = get_local_gradle_wrapper_jar()
    write_binary_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.jar"), jar_data)

    # gradle-wrapper.properties
    write_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.properties"), """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.6-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # gradlew (Linux/macOS)
    write_file(os.path.join(root, "gradlew"), """#!/bin/bash
APP_HOME="$(cd "$(dirname "$0")" && pwd)"
CLASSPATH="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"
exec java -Xmx64m -Xms64m -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
""")
    os.chmod(os.path.join(root, "gradlew"), 0o755)

    # gradlew.bat (Windows)
    write_file(os.path.join(root, "gradlew.bat"), r"""@echo off
set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_HOME=%DIRNAME%
set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar
set JAVA_EXE=java
if exist "%JAVA_HOME%\bin\java.exe" set JAVA_EXE=%JAVA_HOME%\bin\java.exe
"%JAVA_EXE%" -Xmx64m -Xms64m -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
""")

    print(f"\n[SUCCESS] 项目 '{PROJECT_NAME}' 生成成功！")
    print(f"\n[NEXT] 下一步：")
    print(f"   cd {PROJECT_NAME}")
    print(f"   ./gradlew assembleDebug")
    print(f"\n[APK] APK 路径: app/build/outputs/apk/debug/app-debug.apk")

if __name__ == "__main__":
    # 检查 Java（仅提示）
    try:
        import subprocess
        subprocess.run(["java", "-version"], capture_output=True, check=True)
    except:
        print("[WARN] 警告: 未检测到 Java，构建时可能失败。请确保 CI 环境有 JDK 17+")
    
    main()
