#!/usr/bin/env python3
"""
Automatically generates a self-contained build_ffzytv.py script
with embedded gradle-wrapper.jar from official Gradle 8.6 distribution.
No internet required after generation!
"""

import os
import sys
import urllib.request
import zipfile
import io
import base64
import tempfile

# URL to official Gradle 8.6 binary distribution
GRADLE_URL = "https://services.gradle.org/distributions/gradle-8.6-bin.zip"
WRAPPER_JAR_PATH = "gradle-8.6/gradle/wrapper/gradle-wrapper.jar"

def download_and_extract_jar():
    print("📥 Downloading gradle-8.6-bin.zip (only partial fetch for efficiency)...")
    try:
        with urllib.request.urlopen(GRADLE_URL) as response:
            # Read entire ZIP into memory (≈120MB, acceptable for CI)
            zip_data = response.read()
    except Exception as e:
        print(f"❌ Failed to download Gradle: {e}", file=sys.stderr)
        sys.exit(1)

    print("📦 Extracting gradle-wrapper.jar from ZIP...")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            jar_data = zf.read(WRAPPER_JAR_PATH)
        print(f"✅ Extracted {len(jar_data)} bytes.")
        return jar_data
    except KeyError:
        print(f"❌ Path not found in ZIP: {WRAPPER_JAR_PATH}", file=sys.stderr)
        sys.exit(1)

def encode_to_base64(data):
    b64 = base64.b64encode(data).decode('ascii')
    print("🔑 Encoding to base64...")
    return b64

def generate_build_script(jar_b64):
    script_content = f'''#!/usr/bin/env python3
import os
import subprocess
import sys
import base64
from PIL import Image, ImageDraw

# Embedded gradle-wrapper.jar for Gradle 8.6 (official)
GRADLE_WRAPPER_JAR_B64 = """{jar_b64}"""

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
    gradle_wrapper_jar = os.path.join(root, "gradle", "wrapper", "gradle-wrapper.jar")

    os.makedirs(java_root, exist_ok=True)
    for d in ["values", "layout", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # gradle.properties
    write_file(os.path.join(root, "gradle.properties"), "android.useAndroidX=true\\norg.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\\n")

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
rootProject.name = '{{PROJECT_NAME}}'
include ':app'
""")

    # root build.gradle
    write_file(os.path.join(root, "build.gradle"), "plugins {{\\n    id 'com.android.application' version '8.3.0' apply false\\n}}\\n")

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
    write_file(os.path.join(res, "values", "strings.xml"), "<resources>\\n    <string name=\\"app_name\\">FFZYTV</string>\\n</resources>\\n")
    
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
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }
}
""")

    # Icons
    ic_launcher = create_icon("FF", 192, (70, 130, 180), (255, 255, 255))
    banner = create_icon("FFZYTV", 320, (41, 128, 185), (255, 255, 255))
    ic_launcher.save(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"))
    banner.save(os.path.join(res, "drawable", "banner.png"))

    # Write gradle-wrapper.jar
    print("📦 Writing gradle-wrapper.jar...")
    try:
        jar_data = base64.b64decode(GRADLE_WRAPPER_JAR_B64.strip())
        write_binary_file(gradle_wrapper_jar, jar_data)
    except Exception as e:
        print(f"❌ Failed to write gradle-wrapper.jar: {{e}}", file=sys.stderr)
        sys.exit(1)

    # gradle-wrapper.properties
    write_file(os.path.join(root, "gradle", "wrapper", "gradle-wrapper.properties"), """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\\\://services.gradle.org/distributions/gradle-8.6-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # gradlew
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

APP_NAME="Gradle"
APP_BASE_NAME=`basename "$0"`
DEFAULT_JVM_OPTS="-Xmx64m -Xms64m"

warn () { echo "$*"; }
die () { echo; echo "$*"; echo; exit 1; }

cygwin=false; msys=false; darwin=false; nonstop=false
case "`uname`" in
  CYGWIN* ) cygwin=true ;;
  Darwin* ) darwin=true ;;
  MINGW* ) msys=true ;;
  NONSTOP* ) nonstop=true ;;
esac

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar

if [ -n "$JAVA_HOME" ] ; then
  JAVACMD="$JAVA_HOME/bin/java"
  [ ! -x "$JAVACMD" ] && die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME"
else
  JAVACMD="java"
  which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command found."
fi

exec "$JAVACMD" $DEFAULT_JVM_OPTS $JAVA_OPTS $GRADLE_OPTS \\
  -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
"""
    write_file(os.path.join(root, "gradlew"), GRADLEW_CONTENT)
    os.chmod(os.path.join(root, "gradlew"), 0o755)

    # Keystore
    if not os.path.exists(keystore_path):
        print("🔑 Generating keystore...")
        try:
            subprocess.run([
                "keytool", "-genkeypair",
                "-v", "-storetype", "PKCS12",
                "-keystore", keystore_path,
                "-alias", "ffzytv",
                "-keyalg", "RSA", "-keysize", "2048",
                "-validity", "10000",
                "-dname", "CN=FFZYTV, OU=TV, O=FFZY, C=CN",
                "-storepass", "mypassword",
                "-keypass", "mypassword"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"⚠️ Keystore failed: {{e}}", file=sys.stderr)

    print(f"\\n✅ Project '{{PROJECT_NAME}}' ready!")
    print(f"📁 Run: cd {{PROJECT_NAME}} && ./gradlew --version")

if __name__ == "__main__":
    main()
'''
    return script_content

def main():
    print("🚀 Starting auto-generation of build_ffzytv.py...")
    jar_data = download_and_extract_jar()
    jar_b64 = encode_to_base64(jar_data)
    script = generate_build_script(jar_b64)

    output_file = "build_ffzytv.py"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(script)
    
    print(f"\n🎉 Success! Generated: {os.path.abspath(output_file)}")
    print("You can now run:")
    print(f"  python {output_file}")

if __name__ == "__main__":
    main()
