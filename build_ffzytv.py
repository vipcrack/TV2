#!/usr/bin/env python3
import os
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
    # Use default font (Pillow built-in)
    draw.text((size // 2, size // 2), text, fill=fg, anchor="mm")
    return img

def main():
    root = PROJECT_NAME
    app_dir = os.path.join(root, "app")
    src = os.path.join(app_dir, "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")

    # Create all necessary directories
    os.makedirs(java_root, exist_ok=True)
    for d in ["values", "layout", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # === Overwrite settings.gradle ===
    write_file(os.path.join(root, "settings.gradle"), f"""\
rootProject.name = '{PROJECT_NAME}'
include ':app'
""")

    # === Overwrite root build.gradle ===
    write_file(os.path.join(root, "build.gradle"), """\
plugins {
    id 'com.android.application' version '8.3.0' apply false
}
""")

    # === App-level build.gradle ===
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
            storePassword System.getenv("KEYSTORE_PASSWORD") ?: "mypassword"
            keyAlias System.getenv("KEY_ALIAS") ?: "ffzytv"
            keyPassword System.getenv("KEY_PASSWORD") ?: "mypassword"
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
    ic_launcher = create_icon("FF", 192, (70, 130, 180), (255, 255, 255))  # xxxhdpi = 192x192
    banner = create_icon("FFZYTV", 320, (41, 128, 185), (255, 255, 255))

    ic_launcher.save(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"))
    banner.save(os.path.join(res, "drawable", "banner.png"))

    print(f"✅ Android TV project '{PROJECT_NAME}' generated successfully!")

if __name__ == "__main__":
    main()
