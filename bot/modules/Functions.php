<?php

function csvToArray($csvFile){
    $file_to_read = fopen($csvFile, 'r');
    while (!feof($file_to_read) ) {
        $lines[] = fgetcsv($file_to_read);
    }
    fclose($file_to_read);
    return $lines;
}
function color($color = "random" , $text) {
    $arrayColor = array(
        'grey' 		=> '1;30',
        'red' 		=> '1;31',
        'green' 	=> '1;32',
        'yellow' 	=> '1;33',
        'blue' 		=> '1;34',
        'purple' 	=> '1;35',
        'nevy' 		=> '1;36',
        'cyan' 		=> '0;36',
        'white' 	=> '1;1',
        'bgred' 	=> '1;41',
        'bggreen' 	=> '1;42',
        'bgyellow' 	=> '1;43',
        'bgblue' 	=> '1;44',
        'bgpurple' 	=> '1;45',
        'bgnavy' 	=> '1;46',
        'bgwhite' 	=> '1;47'
    );
    return "\033[".$arrayColor[$color]."m".$text."\033[0m";
}
function check_status($name, $type) {
    $ch = curl_init();
    $postdata = http_build_query([
        'name' => $name,
        'type' => $type
    ]);
    curl_setopt($ch, CURLOPT_URL,"https://www.ezv.app/api/secret/bot/listing/check");
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
    curl_setopt($ch, CURLOPT_USERAGENT, base64_encode('JAMAL_Bot v4.0'));
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postdata);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

    $server_output = curl_exec($ch);

    curl_close($ch);
    return $server_output;
}
function stuck($msg) {
    echo color("nevy","[JAMALBOT] ❱❱ ").color("purple", $msg);
    $answer = rtrim(fgets(STDIN));
    return $answer;
}
function format_string($text = "" , $status_data = "") {
    $s  = 25;
    $ar = str_split($text);
    $data = '';
    for ($i=0; $i <$s; $i++) {
        if(isset($ar[$i]) == NULL){
            $data .= ' ';
        }else{
            $data .= $ar[$i];
        }
    }
    return $data." ".$status_data."\n";
}
function parseStr($string, $start, $end) {
    $str = explode($start, $string);
    $str = explode($end, $str[1]);
    return $str[0];
}
function cover() {
    $template = color("blue" , "████████████████████████████████████████████████████████████████████████████████████████████████████████\n");
    $template .= color("blue" , "██                                                                                                    ██\n");
    $template .= color("blue" , "██    ".color("purple" , "    _____   ______   __       __   ______   __              _______    ______   ________ ")."       ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "   /     | /      \ /  \     /  | /      \ /  |            /       \  /      \ /        |")."       ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "   $$$$$ |/$$$$$$  |$$  \   /$$ |/$$$$$$  |$$ |            $$$$$$$  |/$$$$$$  |$$$$$$$$/")."        ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "      $$ |$$ |__$$ |$$$  \ /$$$ |$$ |__$$ |$$ |            $$ |__$$ |$$ |  $$ |   $$ |")."          ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , " __   $$ |$$    $$ |$$$$  /$$$$ |$$    $$ |$$ |            $$    $$< $$ |  $$ |   $$ |")."          ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "/  |  $$ |$$$$$$$$ |$$ $$ $$/$$ |$$$$$$$$ |$$ |            $$$$$$$  |$$ |  $$ |   $$ |")."          ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "$$ \__$$ |$$ |  $$ |$$ |$$$/ $$ |$$ |  $$ |$$ |_____       $$ |__$$ |$$ \__$$ |   $$ |")."          ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "$$    $$/ $$ |  $$ |$$ | $/  $$ |$$ |  $$ |$$       |      $$    $$/ $$    $$/    $$ |")."          ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , " $$$$$$/  $$/   $$/ $$/      $$/ $$/   $$/ $$$$$$$$/       $$$$$$$/   $$$$$$/     $$/")."   V4.0    ".color("blue" , "██")."\n");
    $template .= color("blue" , "██                                                                                                    ██\n");
    $template .= color("blue" , "██    ".color("nevy" , "Coded By: ").color("red" , "Jamal Bigballs")."                                                                        ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("nevy" , "Author URI: ".color("yellow" , "https://www.jamal-bigballs.dev/")."")."                                                     ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("nevy" , "License: ".color("blue" , "GNU General Public License v2 or later")."")."                                                 ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("nevy" , "License URI: ".color("green" , "http://www.gnu.org/licenses/gpl-2.0.html")."")."                                           ".color("blue" , "██")."\n");
    $template .= color("blue" , "██                                                                                                    ██\n");
    $template .= color("blue" , "████████████████████████████████████████████████████████████████████████████████████████████████████████\n");
    return "$template\n";
}
function showStatus($done, $total, $size = 30) {
    static $start_time;
    if ($done > $total)
        return;
    if (empty($start_time))
        $start_time = time();
    $now = time();
    $perc = (double) ($done / $total);
    $bar = floor($perc * $size);
    $status_bar = color("blue" , "\r[");
    $status_bar .= str_repeat(color("purple" , "="), $bar);
    if ($bar < $size) {
        $status_bar .= color("blue" , ">");
        $status_bar .= str_repeat(" ", $size - $bar);
    } else {
        $status_bar .= color("purple" , "=");
    }
    $disp = number_format($perc * 100, 0);
    $status_bar .= color("blue" , "]").color("blue" , " $disp%  $done/$total");
    $rate = ($now - $start_time) / $done;
    $left = $total - $done;
    $eta = round($rate * $left, 2);
    $elapsed = $now - $start_time;
    $status_bar .= color("blue" , " remaining: " . number_format($eta) . " sec. elapsed: " . number_format($elapsed) . " sec.");
    echo "$status_bar  \n";
    flush();
    if ($done == $total) {
        echo "\n";
    }
}
function build_data_files($boundary, $fields, $files) {
    $data = '';
    $eol = "\r\n";
    $delimiter = '-------------' . $boundary;
    foreach ($fields as $name => $content) {
        $data .= "--" . $delimiter . $eol . 'Content-Disposition: form-data; name="' . $name . "\"".$eol.$eol . $content . $eol;
    }
    foreach ($files as $name => $content) {
        $data .= "--" . $delimiter . $eol . 'Content-Disposition: form-data; name="' . $name . '"; filename="' . $name . '"' . $eol . 'Content-Transfer-Encoding: binary'.$eol;
        $data .= $eol;
        $data .= $content . $eol;
    }
    $data .= "--" . $delimiter . "--".$eol;
    return $data;
}
