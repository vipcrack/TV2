#!/usr/bin/env python3
"""
FFZYTV - Final Fixed Android TV App Generator (Leanback 1.0.0 Compatible)
- Uses BrowseSupportFragment + FragmentActivity (correct for leanback:1.0.0)
- Adds appcompat & fragment dependencies
- No more "cannot find symbol" errors
"""

import os
import sys
import base64

PROJECT_NAME = "FFZYTV"
PACKAGE_NAME = "com.ffzy.tv"

def get_local_gradle_wrapper_jar():
    jar_path = os.path.join("assets", "gradle-wrapper.jar")
    if not os.path.isfile(jar_path):
        print(f"[ERROR] Missing: {jar_path}", file=sys.stderr)
        print("[INFO] Please run locally and commit:")
        print("  ./gradlew wrapper --gradle-version 8.6")
        print("  mkdir -p assets && cp gradle/wrapper/gradle-wrapper.jar assets/")
        sys.exit(1)
    with open(jar_path, 'rb') as f:
        return f.read()

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def write_binary_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)

def main():
    print("[BUILD] Generating FFZYTV (LEANBACK 1.0.0 COMPATIBLE VERSION)...")

    root = PROJECT_NAME
    app_dir = os.path.join(root, "app")
    src = os.path.join(app_dir, "src", "main")
    java_root = os.path.join(src, "java", *PACKAGE_NAME.split("."))
    res = os.path.join(src, "res")

    os.makedirs(java_root, exist_ok=True)
    for d in ["values", "drawable", "mipmap-xxxhdpi"]:
        os.makedirs(os.path.join(res, d), exist_ok=True)

    # === gradle.properties ===
    write_file(os.path.join(root, "gradle.properties"), 
               "android.useAndroidX=true\norg.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n")

    # === settings.gradle ===
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

    # === root build.gradle ===
    write_file(os.path.join(root, "build.gradle"), 
               "plugins {\n    id 'com.android.application' version '8.3.0' apply false\n}\n")

    # === app build.gradle ===
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
    implementation 'androidx.leanback:leanback:1.0.0'

    // REQUIRED for AppCompatActivity and FragmentActivity
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.fragment:fragment:1.6.2'

    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'org.jsoup:jsoup:1.17.2'
    implementation 'com.squareup.picasso:picasso:2.8'
    implementation 'com.google.android.exoplayer:exoplayer:2.19.1'
}}
""")

    # === AndroidManifest.xml ===
    write_file(os.path.join(src, "AndroidManifest.xml"), f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:banner="@drawable/banner"
        android:theme="@style/Theme.Leanback">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="landscape">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
                <category android:name="android.intent.category.LEANBACK_LAUNCHER"/>
            </intent-filter>
        </activity>

        <activity
            android:name=".PlayerActivity"
            android:screenOrientation="landscape"
            android:configChanges="orientation|keyboardHidden|screenSize"
            android:exported="false"/>
    </application>
</manifest>
""")

    # === strings.xml ===
    write_file(os.path.join(res, "values", "strings.xml"), 
               "<resources>\n    <string name=\"app_name\">FFZYTV</string>\n</resources>\n")

    # === styles.xml (CRITICAL) ===
    write_file(os.path.join(res, "values", "styles.xml"), 
               """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.Leanback" parent="Theme.Leanback" />
</resources>
""")

    # === VideoItem.java ===
    write_file(os.path.join(java_root, "VideoItem.java"), """package com.ffzy.tv;

public class VideoItem {
    public String id;
    public String title;
    public String coverUrl;
    public String detailUrl;

    public VideoItem(String id, String title, String coverUrl, String detailUrl) {
        this.id = id;
        this.title = title;
        this.coverUrl = coverUrl;
        this.detailUrl = detailUrl;
    }
}
""")

    # === ApiService.java ===
    write_file(os.path.join(java_root, "ApiService.java"), """package com.ffzy.tv;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

public class ApiService {
    private static final String BASE_URL = "https://cj.ffzyapi.com";
    private static final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build();

    public static List<VideoItem> fetchCategory(int categoryId) throws IOException {
        String url = BASE_URL + "/index.php/vod/type/id/" + categoryId + ".html";
        Request request = new Request.Builder().url(url).build();
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) throw new IOException("HTTP " + response.code());
            String html = response.body().string();
            Document doc = Jsoup.parse(html);
            List<VideoItem> items = new ArrayList<>();

            Elements links = doc.select("a[href^='/index.php/vod/detail/id/']");
            for (Element a : links) {
                String href = a.attr("href");
                String title = a.text().trim();
                if (title.isEmpty()) continue;
                String id = href.replaceAll(".*/(\\\\d+)\\\\.html", "$1");
                String cover = "https://img.ffzy888.com/" + id + ".jpg";
                items.add(new VideoItem(id, title, cover, href));
            }
            return items;
        }
    }

    public static String extractPlayUrl(String detailHtml) {
        Document doc = Jsoup.parse(detailHtml);
        Element iframe = doc.selectFirst("iframe[src*='m3u8']");
        if (iframe != null) {
            String raw = iframe.attr("src");
            return "https://svip.ffzyplay.com/?url=" + raw;
        }
        return null;
    }
}
""")

    # === CardPresenter.java ===
    write_file(os.path.join(java_root, "CardPresenter.java"), """package com.ffzy.tv;

import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import androidx.leanback.widget.ImageCardView;
import androidx.leanback.widget.Presenter;
import com.squareup.picasso.Picasso;

public class CardPresenter extends Presenter {
    private static final int CARD_WIDTH = 313;
    private static final int CARD_HEIGHT = 176;

    @Override
    public ViewHolder onCreateViewHolder(android.view.ViewGroup parent) {
        ImageCardView cardView = new ImageCardView(parent.getContext());
        cardView.setFocusable(true);
        cardView.setFocusableInTouchMode(true);
        cardView.setMainImageDimensions(CARD_WIDTH, CARD_HEIGHT);
        return new ViewHolder(cardView);
    }

    @Override
    public void onBindViewHolder(ViewHolder viewHolder, Object item) {
        VideoItem video = (VideoItem) item;
        ImageCardView cardView = (ImageCardView) viewHolder.view;
        cardView.setTitleText(video.title);
        cardView.setContentText("");

        ColorDrawable placeholder = new ColorDrawable(Color.parseColor("#EEEEEE"));
        ColorDrawable errorDrawable = new ColorDrawable(Color.parseColor("#CCCCCC"));

        Picasso.get()
            .load(video.coverUrl)
            .placeholder(placeholder)
            .error(errorDrawable)
            .into(cardView.getMainImageView());
    }

    @Override
    public void onUnbindViewHolder(ViewHolder viewHolder) {}
}
""")

    # === MainFragment.java (was MainActivity) ===
    write_file(os.path.join(java_root, "MainFragment.java"), """package com.ffzy.tv;

import android.content.Intent;
import android.os.Bundle;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import androidx.leanback.app.BrowseSupportFragment;
import androidx.leanback.widget.ArrayObjectAdapter;
import androidx.leanback.widget.HeaderItem;
import androidx.leanback.widget.ListRow;
import androidx.leanback.widget.ListRowPresenter;
import androidx.leanback.widget.OnItemViewClickedListener;
import androidx.leanback.widget.Presenter;
import androidx.leanback.widget.Row;
import androidx.leanback.widget.RowPresenter;

public class MainFragment extends BrowseSupportFragment {
    private static final String[] CATEGORIES = {"电影", "连续剧", "综艺", "动漫"};
    private static final int[] CATEGORY_IDS = {1, 2, 3, 4};
    private ArrayObjectAdapter rowsAdapter;
    private ExecutorService executor = Executors.newFixedThreadPool(4);

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);
        setTitle("FFZYTV");

        rowsAdapter = new ArrayObjectAdapter(new ListRowPresenter());
        setAdapter(rowsAdapter);
        setOnItemViewClickedListener(new ItemViewClickedListener());

        loadCategories();
    }

    private void loadCategories() {
        for (int i = 0; i < CATEGORIES.length; i++) {
            final int index = i;
            HeaderItem header = new HeaderItem(CATEGORIES[i]);
            ArrayObjectAdapter listRowAdapter = new ArrayObjectAdapter(new CardPresenter());
            rowsAdapter.add(new ListRow(header, listRowAdapter));

            executor.execute(() -> {
                try {
                    List<VideoItem> items = ApiService.fetchCategory(CATEGORY_IDS[index]);
                    getActivity().runOnUiThread(() -> {
                        for (VideoItem item : items) {
                            listRowAdapter.add(item);
                        }
                    });
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }
    }

    private final class ItemViewClickedListener implements OnItemViewClickedListener {
        @Override
        public void onItemClicked(Presenter.ViewHolder itemViewHolder, Object item,
                                  RowPresenter.ViewHolder rowViewHolder, Row row) {
            VideoItem video = (VideoItem) item;
            Intent intent = new Intent(getActivity(), PlayerActivity.class);
            intent.putExtra("detail_url", "https://cj.ffzyapi.com" + video.detailUrl);
            startActivity(intent);
        }
    }
}
""")

    # === MainActivity.java (now just a container) ===
    write_file(os.path.join(java_root, "MainActivity.java"), """package com.ffzy.tv;

import android.os.Bundle;
import androidx.fragment.app.FragmentActivity;

public class MainActivity extends FragmentActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (savedInstanceState == null) {
            getSupportFragmentManager()
                .beginTransaction()
                .replace(android.R.id.content, new MainFragment())
                .commit();
        }
    }
}
""")

    # === PlayerActivity.java (unchanged, now has appcompat) ===
    write_file(os.path.join(java_root, "PlayerActivity.java"), """package com.ffzy.tv;

import android.content.Context;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.exoplayer2.ExoPlayer;
import com.google.android.exoplayer2.MediaItem;
import com.google.android.exoplayer2.ui.StyledPlayerView;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class PlayerActivity extends AppCompatActivity {
    private StyledPlayerView playerView;
    private ExoPlayer player;
    private ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        playerView = new StyledPlayerView(this);
        setContentView(playerView);

        String detailUrl = getIntent().getStringExtra("detail_url");
        loadAndPlay(detailUrl);
    }

    private void loadAndPlay(String detailUrl) {
        executor.execute(() -> {
            try {
                OkHttpClient client = new OkHttpClient();
                Request request = new Request.Builder().url(detailUrl).build();
                Response response = client.newCall(request).execute();
                String html = response.body().string();
                String playUrl = ApiService.extractPlayUrl(html);

                new Handler(Looper.getMainLooper()).post(() -> {
                    if (playUrl != null) {
                        startPlayback(playUrl);
                    } else {
                        finish();
                    }
                });
            } catch (IOException e) {
                e.printStackTrace();
                finish();
            }
        });
    }

    private void startPlayback(String playUrl) {
        player = new ExoPlayer.Builder(this).build();
        playerView.setPlayer(player);
        MediaItem mediaItem = MediaItem.fromUri(Uri.parse(playUrl));
        player.setMediaItem(mediaItem);
        player.prepare();
        player.play();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (player != null) {
            player.release();
            player = null;
        }
        executor.shutdown();
    }
}
""")

    # === Generate minimal valid icons ===
    tiny_red = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
    write_binary_file(os.path.join(res, "mipmap-xxxhdpi", "ic_launcher.png"), tiny_red)

    tiny_blue = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
    write_binary_file(os.path.join(res, "drawable", "banner.png"), tiny_blue)

    # === Gradle Wrapper ===
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

    print(f"\n[SUCCESS] FFZYTV project generated (LEANBACK 1.0.0 COMPATIBLE)!")
    print(f"✅ Uses MainFragment + MainActivity (correct architecture)")
    print(f"✅ Added appcompat & fragment dependencies")
    print(f"✅ Theme.Leanback defined")
    print(f"\n[Next steps]")
    print(f"  cd {PROJECT_NAME}")
    print(f"  ./gradlew assembleDebug")
    print(f"  # Install app-debug.apk on雷电模拟器 or Android TV")

if __name__ == "__main__":
    main()
