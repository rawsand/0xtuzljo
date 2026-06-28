<?php

// ===============================
// PLAYLIST LINKS
// ===============================

$playlistLinks = [
    "Link 1" => "https://raw.githubusercontent.com/etcvai/ExtenderMax/refs/heads/main/iptv.m3u8"
	"Link 2" => "https://clarity-tv.vercel.app/api/playlist/?id=ALLINONE"
];

$allowedFile = "allowed_channels_extendermax.txt";


// ===============================
// FETCH PLAYLIST
// ===============================

function fetchPlaylist($url)
{
    $ch = curl_init();

    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_USERAGENT => "Mozilla/5.0 IPTV Parser"
    ]);

    $data = curl_exec($ch);
    curl_close($ch);

    return $data;
}


// ===============================
// SPLIT EXTINF BLOCKS
// ===============================

function splitBlocks($content)
{
    return preg_split('/(?=#EXTINF)/i', $content, -1, PREG_SPLIT_NO_EMPTY);
}


// ===============================
// LOAD ALLOWED FILE
// Format:
// Channel : Link : Search Group : Replace Group
// ===============================

$allowedLines = file($allowedFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

$allowed = [];

foreach ($allowedLines as $line) {

    $parts = explode(":", $line, 4);

    if (count($parts) < 4) continue;

    $channel = strtolower(trim($parts[0]));
    $link    = trim($parts[1]);
    $group   = strtolower(trim($parts[2]));
    $newGrp  = trim($parts[3]);

    $channel = preg_replace('/\s+/', ' ', $channel);
    $group   = preg_replace('/\s+/', ' ', $group);

    $allowed[$link][] = [
        "channel" => $channel,
        "group"   => $group,
        "newgrp"  => $newGrp
    ];
}

// ===============================
// PROCESS PLAYLISTS
// ===============================

$outputFile = "8b249zhj3vg65us_mix.m3u";
file_put_contents($outputFile, "#EXTM3U\n");

// ===============================
// PROCESS PLAYLISTS
// ===============================

foreach ($playlistLinks as $linkName => $url) {

    if (!isset($allowed[$linkName])) continue;

    $playlist = fetchPlaylist($url);
    if (!$playlist) continue;

    $blocks = splitBlocks($playlist);

    foreach ($blocks as $block) {

        $extinfLine = strtok($block, "\n");

        if (!$extinfLine) continue;
        if (stripos($extinfLine, '#EXTINF') !== 0) continue;

        // Extract channel name
        $parts = explode(",", $extinfLine);
        $channelName = strtolower(trim(end($parts)));
        $channelName = preg_replace('/\s+/', ' ', $channelName);

        // Extract group title
        $groupTitle = '';
        if (preg_match('/group-title="([^"]+)"/i', $extinfLine, $match)) {
            $groupTitle = strtolower(trim($match[1]));
            $groupTitle = preg_replace('/\s+/', ' ', $groupTitle);
        }

        foreach ($allowed[$linkName] as $item) {

            if (
                $channelName === $item['channel'] &&
                $groupTitle === $item['group']
            ) {

                // Replace group title
                $newExtinf = preg_replace(
                    '/group-title="[^"]*"/i',
                    'group-title="'.$item['newgrp'].'"',
                    $extinfLine
                );

                $block = str_replace($extinfLine, $newExtinf, $block);

                file_put_contents($outputFile, trim($block) . "\n\n", FILE_APPEND);

                break;
            }
        }
    }
}

?>