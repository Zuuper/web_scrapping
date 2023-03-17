<?php
error_reporting(E_ALL);

require 'modules/Curl.php';

$config = parse_ini_file("config.ini");
$rollingCurl = new Curl();

echo cover();
bruh:
echo color("nevy",'[+] ').color("purple","=================================").color("nevy",' [+]')."\n";
foreach (["villa", "food", "wow"] as $key => $value) {
    $typeList[] = $value;
    echo color("nevy",'[i] ').color('blue' , trim(format_string($value, "[$key]")))."\n";
}
echo color("nevy",'[+] ').color("purple","=================================").color("nevy",' [+]')."\n\n";
$typ = stuck("Enter the listing type number : ");

if($typ  == '') {
    echo "\n";
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "User cancelled process\n"));
    die();
}
$type = $typeList[$typ];
if(!in_array($type, ["villa", "food", "wow"])) {
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "Invalid data bruhh...\n"));
    goto bruh;
}
switch($type) {
    case 'villa':
        $api_endpoint = $config['api'].$config['villa'];
        break;
    case 'food':
        $api_endpoint = $config['api'].$config['food'];
        break;
    case 'wow':
        $api_endpoint = $config['api'].$config['wow'];
        break;
    default:
        $api_endpoint = $config['api'].$config['villa'];
        break;
}

echo color("nevy","[EZVBOT] ❱❱ ".color('purple', "Looking for an csv file\n"));

$locdir_list = 'csv';
$list_load = scandir($locdir_list);
foreach ($list_load as $key => $value) {
    if(is_file($locdir_list."/".$value) && pathinfo($locdir_list."/".$value, PATHINFO_EXTENSION) == 'csv'){
        $arrayList[] = $locdir_list."/".$value;
    }
}
$media_load = scandir($locdir_list.'/media');
foreach($media_load as $folder) {
    if($folder !== '.' && $folder !== '..') {
        $mediaList = scandir($locdir_list.'/media'.'/'.$folder);
        foreach($mediaList as $media) {
            if($media !== '.' && $media !== '..') {
                $FinalPath[$folder][] = $locdir_list.'/media'.'/'.$folder.'/'.$media;
            }
        }
    }
}
if(count($arrayList) == 0){
    echo color("nevy","[EZVBOT] ❱❱ ".color('bgred', "No csv files found in the \"csv\" folder\n"));
    die();
}
echo color("nevy","[EZVBOT] ❱❱ ".color('green', "There are ".count($arrayList)." csv files.")."\n\n");
bruhh:
echo color("nevy",'[+] ').color("purple","=================================").color("nevy",' [+]')."\n";
foreach ($arrayList as $key => $value) {
    echo color("nevy",'[i] ').color('blue' , trim(format_string(pathinfo($value)['basename'] , "[$key]")))."\n";
}
echo color("nevy",'[+] ').color("purple","=================================").color("nevy",' [+]')."\n\n";

$pil = stuck("Enter the csv files number : ");

if($pil == '') {
    echo "\n";
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "User cancelled process\n"));
    die();
}
if(!file_exists($arrayList[$pil])) {
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "Invalid data bruhh...\n"));
    goto bruhh;
}

$csv = csvToArray($arrayList[$pil]);
$countList = count($csv);
echo color("nevy","[EZVBOT] ❱❱ ".color('blue', "Found ({$countList}) data in {$arrayList[$pil]}\n"));

bruhhh:
$amount_listing = stuck("Enter amount to add listing (min: 2) : ");

if($amount_listing  == '') {
    echo "\n";
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "User cancelled process\n"));
    die();
}
if((int)$amount_listing < 2) {
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "Minimum 2 listings\n"));
    goto bruhhh;
}
if((int)$amount_listing > $countList) {
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "Are u drunk bruh?\n"));
    goto bruhhh;
}

echo color("nevy","[EZVBOT] ❱❱ ".color('blue', "Listing to add: {$amount_listing} data\n"));
echo color("nevy","[EZVBOT] ❱❱ ".color('blue', "Processing data...\n"));

for ($i = 1; $i <= (int)$amount_listing; $i++) {

    if(isset($csv[$i][0]) && $type == 'food') {
        $name = $dec = $addr = $loc = $prc = $s_cat = $lat = $lon = [];

        if(!empty(trim($csv[$i][1]))) {
            $maps = gratisan($csv[$i][1]);
            if(isset($maps['error'])) {
                unset($maps);
            }
            $name = ['name' => trim($csv[$i][1])];
        }
        if(!empty(trim($csv[$i][7]))) {
            $dec = ['short_description' => trim($csv[$i][7])];
        }
        if(!empty(trim($csv[$i][6]))) {
            $maps = gratisan($csv[$i][6]);
            if(isset($maps['error'])) {
                unset($maps);
                $maps = 'error';
            }
            $addr = ['address' => trim($csv[$i][6])];
        }
        if(!empty(trim($csv[$i][4]))) {
            $prc = ['id_price' => strlen(trim($csv[$i][4]))];
        }
        if(!empty(trim($csv[$i][5]))) {
            $s_cat = ['sub_cat' => trim($csv[$i][5])];
        }
        if($maps !== 'error') {
            if(!empty(trim($maps[0]['address']['county']))) {
                $loc = ['location' => trim($maps[0]['address']['county'])];
            }
            if(!empty(trim($maps[0]['lat']))) {
                $lat = ['lat' => trim($maps[0]['lat'])];
            }
            if(!empty(trim($maps[0]['lon']))) {
                $lon = ['lon' => trim($maps[0]['lon'])];
            }
        }
        $files = [];
        foreach ($FinalPath[$csv[$i][1]] as $file) {
            $files[$file] = file_get_contents($file);
        }
        $textData = array_merge($name, $dec, $addr, $loc, $prc, $s_cat, $lat, $lon);

        if(is_null($textData)) {
            $textData = [
                'name' => trim($csv[$i][1]),
                'short_description' => trim($csv[$i][7]),
                'address' => trim($csv[$i][6]),
                'id_price' => strlen(trim($csv[$i][4])),
                'sub_cat' => trim($csv[$i][5]),
                'location' => trim($maps[0]['address']['county']),
                'lat' => trim($maps[0]['lat']),
                'lon' => trim($maps[0]['lon'])
            ];
        }
    }

    $boundary = uniqid();
    $delimiter = '-------------' . $boundary;
    $post_data = build_data_files($boundary, $textData, $files);
    // $post_data = $textData;
    $headers = ["Content-Type: multipart/form-data; boundary=" . $delimiter, "Content-Length: " . strlen($post_data)];

    $rollingCurl->setOptions([
        CURLOPT_HEADER => 0,
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_SSL_VERIFYHOST => 0,
        CURLOPT_SSL_VERIFYPEER => 0,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_USERAGENT => base64_encode('EZV_Bot v1.1')
    ])->post($api_endpoint, $post_data);
    showStatus($i, (int)$amount_listing, 38);
}
$start = microtime(true);
echo color("nevy","[EZVBOT] ❱❱ ".color('green', "Starting process...\n\n"));
$tot = 1;
$rollingCurl->setCallback(function(Request $request, Curl $Curl) {
    global $config, $tot, $type;

    $status = json_decode($request->getResponseText(), true);
    if($status['status'] == 'success') {
        if($type == 'food') {
            echo color("purple","[+]========[Success Add ({$tot})]========[+]\n");
            echo color("blue", format_string('[i] ID Restaurant', color("green", ": {$status['data']}")));
            echo color("blue", format_string('[i] Name', color("green", ": {$status['name']}")));
            echo color("blue", format_string('[i] ID Price', color("green", ": {$status['id_price']}")));
            echo color("blue", format_string('[i] Address', color("green", ": {$status['address']}")));
            echo color("blue", format_string('[i] Latitude & Longitude', color("green", ": {$status['latitude']} / {$status['longitude']}")));
            echo color("blue", format_string('[i] Url', color("green", ": {$config['url_food']}{$status['data']}")));
            echo color("blue", format_string('[i] Location', color("green", ": {$status['id_location']}")));
            echo color("blue", format_string('[i] Short Description', color("green", ": {$status['short_short_description']}")));
            echo color("blue", format_string('[i] Gallery', color("green", ": {$status['gallery_photo']}")));
            file_put_contents('logs/success.log', "Restaurant {$status['data']}: {$status['name']}\n", FILE_APPEND | LOCK_EX);
            $tot++;
        }
    } else {
        $error = $status['status'] ?? parseStr($request->getResponseText(), '<title>', '</title>');
        $sname = $status['name'] ?? $error;
        echo color("purple","[+]========[Something error]========[+]\n");
        echo color("red","[i] Error: {$error}\n");
        file_put_contents('logs/error.log', "Restaurant: {$sname}\n", FILE_APPEND | LOCK_EX);
        $tot++;
    }
    file_put_contents('logs/debug.log', "=================================\nBruhh: ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
    $Curl->clearCompleted();
    $Curl->prunePendingRequestQueue();
})->setSimultaneousLimit((int)$amount_listing)->execute();
echo color("purple","[+]=================================[+]\n\n");
echo color("nevy","[EZVBOT] ❱❱ ".color('green', "Finish in " . (microtime(true) - $start) . " seconds\n\n"));

function csvToArray($csvFile){
    $file_to_read = fopen($csvFile, 'r');
    while (!feof($file_to_read) ) {
        $lines[] = fgetcsv($file_to_read);
    }
    fclose($file_to_read);
    return $lines;
}
// function getLatLngFromGoogle($address) {
//     $API_KEY = "X_X";
//     $url = "https://maps.google.com/maps/api/geocode/json?address=".urlencode($address)."&sensor=false&region=bali&key=".$API_KEY;
//     $ch = curl_init();
//     curl_setopt($ch, CURLOPT_URL, $url);
//     curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
//     curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
//     curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
//     $response = curl_exec($ch);
//     curl_close($ch);
//     $returnBody = json_decode($response);

//     $status = $returnBody->status;
//     if($status == "REQUEST_DENIED"){
//         $data['error'] = $returnBody->error_message;
//     } else {
//         $data['lat'] = $returnBody->results[0]->geometry->location->lat;
//         $data['lng'] = $returnBody->results[0]->geometry->location->lng;
//     }
//     return $data;
// }
function gratisan($addr) {
    $curl = curl_init('https://us1.locationiq.com/v1/search?key=pk.439605fe6e94cf67f81e1934e4bde486&q='.urlencode($addr).'&limit=1&addressdetails=1&countrycodes=id&format=json');

    curl_setopt_array($curl, array(
      CURLOPT_RETURNTRANSFER    =>  true,
      CURLOPT_FOLLOWLOCATION    =>  true,
      CURLOPT_MAXREDIRS         =>  10,
      CURLOPT_TIMEOUT           =>  30,
      CURLOPT_CUSTOMREQUEST     =>  'GET',
    ));

    $response = curl_exec($curl);
    $err = curl_error($curl);

    curl_close($curl);

    if ($err) {
      echo 'cURL Error #:' . $err;
    } else {
      $data = json_decode($response, true);
      if(isset($data['error'])) {
        return ['error' => $data['error'], 'address' => $addr];
      } else {
        return $data;
      }
    }
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
function stuck($msg) {
    echo color("nevy","[EZVBOT] ❱❱ ").color("purple",$msg);
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
    $template = color("blue" , "███████████████████████████████████████████████████████████████████████████████\n");
    $template .= color("blue" , "██                                                                           ██\n");
    $template .= color("blue" , "██    ".color("purple" , "███████╗███████╗██╗   ██╗    ██████╗  ██████╗ ████████╗")."                ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "██╔════╝╚══███╔╝██║   ██║    ██╔══██╗██╔═══██╗╚══██╔══╝")."                ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "█████╗    ███╔╝ ██║   ██║    ██████╔╝██║   ██║   ██║")."                   ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "██╔══╝   ███╔╝  ╚██╗ ██╔╝    ██╔══██╗██║   ██║   ██║")."                   ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "███████╗███████╗ ╚████╔╝     ██████╔╝╚██████╔╝   ██║")."                   ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("purple" , "╚══════╝╚══════╝  ╚═══╝      ╚═════╝  ╚═════╝    ╚═╝")."   V1.0            ".color("blue" , "██")."\n");
    $template .= color("blue" , "██                                                                           ██\n");
    $template .= color("blue" , "██    ".color("nevy" , "Coded By :")." ".color("red" , "Jamal Bigballs")."                                              ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("nevy" , "Author URI: ".color("cyan" , "https://www.jamal-bigballs.dev/")."")."                            ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("nevy" , "License: ".color("cyan" , "GNU General Public License v2 or later")."")."                        ".color("blue" , "██")."\n");
    $template .= color("blue" , "██    ".color("nevy" , "License ".color("cyan" , "URI: http://www.gnu.org/licenses/gpl-2.0.html")."")."                  ".color("blue" , "██")."\n");
    $template .= color("blue" , "██                                                                           ██\n");
    $template .= color("blue" , "███████████████████████████████████████████████████████████████████████████████\n");
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
    echo "$status_bar  ";
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
