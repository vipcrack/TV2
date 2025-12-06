#!/usr/bin/env python3
import os
import subprocess
import sys
from PIL import Image, ImageDraw

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_icon(text, size, bg, fg):
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    draw.text((size // 2, size // 2), text, fill=fg, anchor="mm")
    return img

def main():
    root = PROJECT_NAME
    app_dir = os.path.join(root, "app")
    src = os.path.join(app_dir, "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")
    keystore_path = os.path.join(app_dir, "ffzytv.keystore")

    # Create directories
    os.makedirs(java_root, exist_ok=True)
    for d in ["values", "layout", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # === gradle.properties ===
    write_file(os.path.join(root, "gradle.properties"), """\
android.useAndroidX=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
""")

    # === settings.gradle ===
    write_file(os.path.join(root, "settings.gradle"), f"""\
pluginManagement {{
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

    # === Root build.gradle ===
    write_file(os.path.join(root, "build.gradle"), """\
plugins {
    id 'com.android.application' version '8.3.0' apply false
}
""")

    # === App build.gradle ===
    write_file(os.path.join(app_dir, "build.gradle"), f"""\
plugins {{
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
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
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

    # === AndroidManifest.xml ===
    write_file(os.path.join(src, "AndroidManifest.xml"), f"""\
<?xml version="1.0" encoding="utf-8"?>
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

    # === strings.xml ===
    write_file(os.path.join(res, "values", "strings.xml"), """\
<resources>
    <string name="app_name">FFZYTV</string>
</resources>
""")

    # === MainActivity.java ===
    write_file(os.path.join(java_root, "MainActivity.java"), """\
package com.ffzy.tv;

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

    # === activity_main.xml ===
    write_file(os.path.join(res, "layout", "activity_main.xml"), """\
<?xml version="1.0" encoding="utf-8"?>
<TextView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:text="FFZYTV\\nhttps://cj.ffzyapi.com/"
    android:textColor="#FFFFFF"
    android:background="#2C3E50"/>
""")

    # === Generate icons ===
    ic_launcher = create_icon("FF", 192, (70, 130, 180), (255, 255, 255))
    banner = create_icon("FFZYTV", 320, (41, 128, 185), (255, 255, 255))
    ic_launcher.save(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"))
    banner.save(os.path.join(res, "drawable", "banner.png"))

    # === Gradle Wrapper ===
    gradle_wrapper_dir = os.path.join(root, "gradle", "wrapper")
    os.makedirs(gradle_wrapper_dir, exist_ok=True)
    write_file(os.path.join(gradle_wrapper_dir, "gradle-wrapper.properties"), """\
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.6-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # === 自动生成 keystore（仅当不存在时）===
    if not os.path.exists(keystore_path):
        print("🔑 正在生成测试用 keystore: ffzytv.keystore ...")
        try:
            subprocess.run([
                "keytool", "-genkeypair",
                "-v",
                "-storetype", "PKCS12",
                "-keystore", keystore_path,
                "-alias", "ffzytv",
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-dname", "CN=FFZYTV, OU=TV, O=FFZY, C=CN",
                "-storepass", "mypassword",
                "-keypass", "mypassword"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ keystore 生成成功！")
        except FileNotFoundError:
            print("❌ 错误: 未找到 'keytool'，请确保已安装 JDK 并将其加入 PATH。", file=sys.stderr)
            print("💡 提示: 在 Ubuntu/Debian 上可运行: sudo apt install openjdk-17-jdk", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ keystore 生成失败: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("ℹ️  keystore 已存在，跳过生成。")

    print(f"\n✅ Android TV 项目 '{PROJECT_NAME}' 生成完毕！")
    print("✅ 可直接运行以下命令构建 Release APK：")
    print(f"   cd {PROJECT_NAME} && ./gradlew assembleRelease --no-daemon")
    print("\n📦 输出路径: app/build/outputs/apk/release/app-release.apk")

if __name__ == "__main__":
    main()
