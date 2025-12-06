#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def write_image(path, img):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG")

def create_text_image(width, height, text, bg_color, text_color):
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=min(width, height) // 3)
    except:
        font = ImageFont.load_default()
    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        w, h = draw.textsize(text, font=font)
    x, y = (width - w) // 2, (height - h) // 2
    draw.text((x, y), text, fill=text_color, font=font)
    return img

def main():
    root = PROJECT_NAME
    src = os.path.join(root, "app", "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")

    # settings.gradle
    write_file(os.path.join(root, "settings.gradle"), f"rootProject.name = '{PROJECT_NAME}'\ninclude ':app'\n")

    # Project build.gradle
    write_file(os.path.join(root, "build.gradle"), """\
plugins {
    id 'com.android.application' version '8.3.0' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.20' apply false
}
""")

    # App build.gradle
    write_file(os.path.join(root, "app", "build.gradle"), f"""\
plugins {{
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
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
    kotlinOptions {{
        jvmTarget = '17'
    }}
    buildFeatures {{
        compose true
    }}
    composeOptions {{
        kotlinCompilerExtensionVersion '1.5.10'
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.activity:activity-compose:1.8.2'
    implementation platform('androidx.compose:compose-bom:2024.04.01')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.material3:material3:1.2.1'
    implementation 'androidx.tv:tv-foundation:1.0.0-alpha06'
    implementation 'androidx.tv:tv-material:1.0.0-alpha06'
    implementation 'com.squareup.retrofit2:retrofit:2.11.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.11.0'
    implementation 'io.coil-kt:coil-compose:2.7.0'
    implementation 'androidx.datastore:datastore-preferences:1.1.1'
    implementation 'androidx.leanback:leanback-preference:1.1.0'
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
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:banner="@drawable/banner"
            android:logo="@mipmap/ic_launcher">
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

    # styles.xml
    write_file(os.path.join(res, "values", "styles.xml"), '<resources>\n<style name="AppTheme" parent="android:Theme.Material.NoActionBar"/>\n</resources>')

    # Minimal MainActivity.kt (just to make it buildable)
    write_file(os.path.join(java_root, "MainActivity.kt"), """\
package com.ffzy.tv
import android.app.Activity
import android.os.Bundle
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
""")

    # Dummy layout
    write_file(os.path.join(res, "layout", "activity_main.xml"), """\
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="FFZYTV\nLoading from https://cj.ffzyapi.com/"
        android:layout_gravity="center"
        android:textSize="24sp"
        android:textColor="#FFFFFF"
        android:background="#2C3E50"/>
</FrameLayout>
""")

    # Generate icons
    launcher = create_text_image(144, 144, "FF", (70, 130, 180, 255), (255, 255, 255, 255))
    banner = create_text_image(320, 180, "FFZYTV", (41, 128, 185, 255), (255, 255, 255, 255))
    write_image(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"), launcher)
    write_image(os.path.join(res, "drawable", "banner.png"), banner)

    print("✅ Project generated at ./" + PROJECT_NAME)

if __name__ == "__main__":
    main()