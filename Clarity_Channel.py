<?php

// ===============================
// PLAYLIST LINKS
// ===============================

$playlistLinks = [
    "Link 1" => "https://clarity-tv.vercel.app/api/playlist/?id=ALLINONE"
];

// ===============================
// OUTPUT FILE
// ===============================

$outputFile = "8b249zhj3vg65us_so.m3u";

// ===============================
// RULES ARRAY (NEW FORMAT)
// Channel : Search Group : Replace Group
// ===============================

$rules = [
    "SET HD SonyLiv : SonyLiv | Entertainment : JioTV+ | Entertainment"
];


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
// START OUTPUT FILE
// ===============================

file_put_contents($outputFile, "");


// ===============================
// PROCESS RULES
// ===============================

foreach ($playlistLinks as $linkName => $url) {

    $playlist = fetchPlaylist($url);
    if (!$playlist) continue;

    $blocks = splitBlocks($playlist);

    foreach ($blocks as $block) {

        $extinfLine = strtok($block, "\n");

        if (!$extinfLine || stripos($extinfLine, '#EXTINF') !== 0) continue;

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

        foreach ($rules as $rule) {

            $parts = explode(":", $rule, 3);

            if (count($parts) < 3) continue;

            $ruleChannel = strtolower(trim($parts[0]));
            $ruleSearch  = strtolower(trim($parts[1]));
            $ruleReplace = trim($parts[2]);

            $ruleChannel = preg_replace('/\s+/', ' ', $ruleChannel);
            $ruleSearch  = preg_replace('/\s+/', ' ', $ruleSearch);

            if (
                $channelName === $ruleChannel &&
                strpos($groupTitle, $ruleSearch) !== false
            ) {

                // Replace group-title
                $newExtinf = preg_replace(
                    '/group-title="[^"]*"/i',
                    'group-title="' . $ruleReplace . '"',
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
