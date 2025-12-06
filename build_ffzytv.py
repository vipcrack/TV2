#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

GRADLEW_CONTENT = '''#!/bin/bash
APP_HOME="$(cd "$(dirname "$0")" && pwd)"
CLASSPATH="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"
if [ ! -f "$CLASSPATH" ]; then
    echo "gradle-wrapper.jar not found. Run 'gradle wrapper' to generate it."
    exit 1
fi
exec java -cp "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
'''

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    root = PROJECT_NAME
    src = os.path.join(root, "app", "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")

    # === 创建所有必要目录 ===
    os.makedirs(java_root, exist_ok=True)
    # 👇 关键修复：提前创建 res 子目录
    for d in ["values", "layout", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # settings.gradle
    write_file(os.path.join(root, "settings.gradle"), f"rootProject.name = '{PROJECT_NAME}'\ninclude ':app'\n")

    # Project build.gradle
    write_file(os.path.join(root, "build.gradle"), """\
plugins {
    id 'com.android.application' version '8.3.0' apply false
}
""")

    # App build.gradle
    write_file(os.path.join(root, "app", "build.gradle"), f"""\
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

    # strings.xml
    write_file(os.path.join(res, "values", "strings.xml"), '<resources>\n<string name="app_name">FFZYTV</string>\n</resources>')

    # MainActivity.java
    write_file(os.path.join(java_root, "MainActivity.java"), """\
package com.ffzy.tv;
import android.app.Activity;
import android.os.Bundle;
public class MainActivity extends Activity {
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }
}
""")

    # activity_main.xml
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

    # Icons
    def create_icon(text, size, bg, fg):
        img = Image.new("RGB", (size, size), bg)
        draw = ImageDraw.Draw(img)
        # Use default font
        draw.text((size // 2, size // 2), text, fill=fg, anchor="mm")
        return img

    ic_launcher = create_icon("FF", 144, (70, 130, 180), (255, 255, 255))
    banner = create_icon("FFZYTV", 320, (41, 128, 185), (255, 255, 255))

    # 👇 现在目录已存在，可安全保存
    ic_launcher.save(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"))
    banner.save(os.path.join(res, "drawable", "banner.png"))

    # gradlew
    write_file(os.path.join(root, "gradlew"), GRADLEW_CONTENT)
    os.chmod(os.path.join(root, "gradlew"), 0o755)

    # gradle-wrapper.properties
    write_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.properties"),
"""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.3-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    print(f"✅ Project generated successfully at ./{PROJECT_NAME}")

if __name__ == "__main__":
    main()
