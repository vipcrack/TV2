#!/usr/bin/env python3
"""
FFZYTV Android 项目自动构建器
- 自动下载 gradle-8.6-bin.zip
- 提取内嵌的 gradle-wrapper.jar
- 生成可直接构建的 Android 项目
- 支持 ./gradlew assembleDebug
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
import base64

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

def download_and_extract_gradle_wrapper_jar():
    """从官方 gradle-8.6-bin.zip 中提取 gradle-wrapper.jar"""
    url = "https://services.gradle.org/distributions/gradle-8.6-bin.zip"
    print("📥 正在从官方源下载 gradle-8.6-bin.zip（约 120MB）...")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "gradle-8.6-bin.zip")
            
            # 下载 ZIP
            def reporthook(blocknum, blocksize, totalsize):
                if totalsize > 0:
                    percent = min(100, (blocknum * blocksize * 100) // totalsize)
                    sys.stdout.write(f"\r⏳ 下载中... {percent}%")
                    sys.stdout.flush()
            urllib.request.urlretrieve(url, zip_path, reporthook)
            print("\n✅ 下载完成！")

            # 解压并查找 gradle-wrapper.jar
            print("🔍 正在提取 gradle-wrapper.jar...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for member in zf.namelist():
                    if member.endswith("lib/plugins/gradle-wrapper-8.6.jar"):
                        jar_data = zf.read(member)
                        print("✅ 提取成功！")
                        return jar_data
                
                raise FileNotFoundError("❌ 未在 ZIP 中找到 gradle-wrapper.jar")
                
    except Exception as e:
        print(f"\n💥 错误: {e}", file=sys.stderr)
        sys.exit(1)

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
            # 尝试使用默认字体
            font = ImageFont.load_default()
            draw.text((size // 2, size // 2), text, fill=fg, anchor="mm", font=font)
        except:
            draw.text((size // 2, size // 2), text, fill=fg, anchor="mm")
        return img
    except ImportError:
        print("⚠️ 未安装 Pillow，跳过图标生成（不影响构建）")
        return None

def main():
    root = PROJECT_NAME
    app_dir = os.path.join(root, "app")
    src = os.path.join(app_dir, "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")

    print("🛠️  正在生成项目结构...")
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

    # === 关键：获取并写入 gradle-wrapper.jar ===
    print("🔑 正在处理 Gradle Wrapper...")
    jar_data = download_and_extract_gradle_wrapper_jar()
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
"%JAVA_EXE%" -Xmx64m -Xms64m -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
""")

    print(f"\n🎉 项目 '{PROJECT_NAME}' 生成成功！")
    print(f"\n🚀 下一步：")
    print(f"   cd {PROJECT_NAME}")
    print(f"   ./gradlew assembleDebug")
    print(f"\n📱 APK 路径: app/build/outputs/apk/debug/app-debug.apk")

if __name__ == "__main__":
    # 检查 Java
    try:
        import subprocess
        subprocess.run(["java", "-version"], capture_output=True, check=True)
    except:
        print("⚠️  警告: 未检测到 Java，构建时可能失败。请安装 JDK 17+")
    
    main()
