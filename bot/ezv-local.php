<?php
/*
    ███████████████████████████████████████████████████████████████████████████████
    ██                                                                           ██
    ██    ███████╗███████╗██╗   ██╗    ██████╗  ██████╗ ████████╗                ██
    ██    ██╔════╝╚══███╔╝██║   ██║    ██╔══██╗██╔═══██╗╚══██╔══╝                ██
    ██    █████╗    ███╔╝ ██║   ██║    ██████╔╝██║   ██║   ██║                   ██
    ██    ██╔══╝   ███╔╝  ╚██╗ ██╔╝    ██╔══██╗██║   ██║   ██║                   ██
    ██    ███████╗███████╗ ╚████╔╝     ██████╔╝╚██████╔╝   ██║                   ██
    ██    ╚══════╝╚══════╝  ╚═══╝      ╚═════╝  ╚═════╝    ╚═╝   V3.0            ██
    ██                                                                           ██
    ██    Coded By: Jamal Bigballs                                               ██
    ██    Author URI: https://www.jamal-bigballs.dev/                            ██
    ██    License: GNU General Public License v2 or later                        ██
    ██    License URI: http://www.gnu.org/licenses/gpl-2.0.html                  ██
    ██                                                                           ██
    ███████████████████████████████████████████████████████████████████████████████

    "Keep Never Tired of Learning"
    Jamal Bigball est.2022
*/
ini_set("memory_limit", "-1");
set_time_limit(0);
error_reporting(0);

require_once 'modules/Curl.php';
require_once 'modules/Functions.php';
require_once 'vendor/autoload.php';

use Graze\ParallelProcess\Pool;
use Symfony\Component\Process\Process;

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
        $mediaList = scandir($locdir_list.'/media/'.$folder);
        foreach($mediaList as $media) {
            if($media !== '.' && $media !== '..') {
                if(is_file($locdir_list.'/media/'.$folder.'/'.$media)) {
                    $FinalPath[$folder][] = $locdir_list.'/media/'.$folder.'/'.$media;
                } else {
                    if(is_dir($locdir_list.'/media/'.$folder.'/menu')) {
                        $menuList = scandir($locdir_list.'/media/'.$folder.'/menu');
                        foreach($menuList as $menu) {
                            if($menu !== '.' && $menu !== '..') {
                                if(is_file($locdir_list.'/media/'.$folder.'/menu/'.$menu)) {
                                    $MenuPath[$folder]['menu'][] = $locdir_list.'/media/'.$folder.'/menu/'.$menu;
                                }
                            }
                        }
                    }
                    if(is_dir($locdir_list.'/media/'.$folder.'/videos')) {
                        $videosList = scandir($locdir_list.'/media/'.$folder.'/videos');
                        foreach($videosList as $videos) {
                            if($videos !== '.' && $videos !== '..') {
                                if(is_file($locdir_list.'/media/'.$folder.'/videos/'.$videos)) {
                                    $videosPath[$folder]['videos'][] = $locdir_list.'/media/'.$folder.'/videos/'.$videos;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
if(count($arrayList) == 0){
    echo color("nevy","[EZVBOT] ❱❱ ".color('red', "No csv files found in the \"csv\" folder\n"));
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

$csv = array_filter(csvToArray($arrayList[$pil]));
$countList = count($csv) - 1;
echo color("nevy","[EZVBOT] ❱❱ ".color('blue', "Found ({$countList}) data in [{$arrayList[$pil]}]\n"));

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
$start = microtime(true);
echo color("nevy","[EZVBOT] ❱❱ ".color('green', "Starting process...\n\n"));

$pool = new Pool();

for ($i = 1; $i <= (int)$amount_listing; $i++) {
    if(isset($csv[$i][0]) !== 'title' && $type == 'villa') {
        $name = $addr = $loc = $phn = $fac = $lat = $lon = [];
        if(!empty(trim($csv[$i][$config['villa_name']], ' '))) {
            $name = ['name' => trim($csv[$i][$config['villa_name']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['villa_address']], ' '))) {
            $addr = ['address' => trim($csv[$i][$config['villa_address']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['villa_location']]))) {
            $loc = ['location' => trim($csv[$i][$config['villa_location']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['villa_coordinate']], ' '))) {
            $cord = explode(', ', $csv[$i][$config['villa_coordinate']]);
            $lat = ['lat' => trim($cord[0], ' ')];
            $lon = ['lon' => trim($cord[1], ' ')];
        }
        if(!empty(trim($csv[$i][$config['villa_facilities']]))) {
            $fac = ['facilities' => trim(str_replace(' | ', '|', $csv[$i][$config['villa_facilities']]), ' ')];
        } else {
            if(!empty(trim($csv[$i][$config['villa_facilities2']]))) {
                $fac = ['facilities' => trim(str_replace(' | ', '|', $csv[$i][$config['villa_facilities2']]), ' ')];
            }
        }
        if(!empty(trim($csv[$i][$config['villa_phone']], ' '))) {
            $phn = ['phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['villa_phone']]), ' ')];
        }
        if(isset($FinalPath)) {
            $dataGallery = array_unique($FinalPath[$csv[$i][0]]);
            $countGallery = count($dataGallery);
        } else {
            $dataGallery = [];
            $countGallery = 0;
        }
        if(isset($videosPath)) {
            $dataStory = array_unique($videosPath[$csv[$i][0]]['videos']);
            $countStory = count($dataStory);
        } else {
            $dataStory = [];
            $countStory = 0;
        }
        if(($countGallery + $countStory) > 20) {
            $getPhoto = preg_grep("/^.*\.(jpeg|jpg|png|webp)$/i", $dataGallery);
            $cutPhoto = array_slice($getPhoto, 0, 15);
            $getStory = preg_grep("/^.*\.(mp4|mov)$/i", $dataStory);
            if(!empty($getStory)) {
                $cutStory = array_slice($getStory, 0, 2);
                $arrayFiles = array_merge($cutPhoto, $cutStory);
            } else {
                $getGalleryStory = preg_grep("/^.*\.(mp4|mov)$/i", $dataGallery);
                if(!empty($getGalleryStory)) {
                    $cutStory = array_slice($getGalleryStory, 0, 2);
                    $arrayFiles = array_merge($cutPhoto, $cutStory);
                } else {
                    $arrayFiles = array_slice($getPhoto, 0, 20);
                }
            }
        } else {
            $arrayFiles = array_merge($dataGallery, $dataStory);
        }

        foreach (array_unique($arrayFiles) as $file) {
            $files[$file] = file_get_contents($file);
        }
        $textData = array_merge($name, $addr, $loc, $fac, $lat, $lon);

        if(is_null($textData)) {
            $cord = explode(', ', $csv[$i][$config['villa_coordinate']]);
            $textData = [
                'name' => trim($csv[$i][$config['villa_name']], ' '),
                'address' => trim($csv[$i][$config['villa_address']], ' '),
                'phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['villa_phone']]), ' '),
                'facilities' => trim($csv[$i][$config['villa_facilities']], ' ') ?? trim($csv[$i][$config['villa_facilities2']], ' '),
                'location' => trim($csv[$i][$config['villa_location']], ' '),
                'lat' => trim($cord[0], ' '),
                'lon' => trim($cord[1], ' ')
            ];
        }
    }
    if(isset($csv[$i][0]) !== 'title'  && $type == 'food') {
        $name = $dec = $addr = $phn = $loc = $prc = $s_cat = $lat = $lon = $opn = $cls = [];
        if(!empty(trim($csv[$i][$config['food_name']], ' '))) {
            $name = ['name' => trim($csv[$i][$config['food_name']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['food_sdesc']], ' '))) {
            $dec = ['short_description' => trim($csv[$i][$config['food_sdesc']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['food_address']], ' '))) {
            $addr = ['address' => trim($csv[$i][$config['food_address']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['food_phone']], ' '))) {
            $phn = ['phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['food_phone']]), ' ')];
        }
        if(!empty(trim($csv[$i][$config['food_price']], ' '))) {
            $prc = ['id_price' => strlen(trim($csv[$i][$config['food_price']], ' ')) == 3 ? 5 : strlen(trim($csv[$i][$config['food_price']], ' '))];
        }
        if(!empty(trim($csv[$i][$config['food_subcat']], ' '))) {
            $s_cat = ['sub_cat' => trim(str_replace('restaurant', '', $csv[$i][$config['food_subcat']]), ' ')];
        }
        if(!empty(trim($csv[$i][$config['food_facilities']]))) {
            $fac = ['facilities' => trim($csv[$i][$config['food_facilities']], ' ')];
        } else {
            if(!empty(trim($csv[$i][$config['food_facilities2']]))) {
                $fac = ['facilities' => trim($csv[$i][$config['food_facilities2']], ' ')];
            }
        }
        if(!empty(trim($csv[$i][$config['food_location']]))) {
            $loc = ['location' => trim($csv[$i][$config['food_location']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['food_coordinate']], ' '))) {
            $cord = explode(', ', $csv[$i][$config['food_coordinate']]);
            $lat = ['lat' => trim($cord[0], ' ')];
            $lon = ['lon' => trim($cord[1], ' ')];
        }
        if(!empty(trim($csv[$i][$config['food_opncls']], ' ')) && trim($csv[$i][$config['food_opncls']], ' ') !== 'Closed') {
            if(trim($csv[$i][$config['food_opncls']], ' ') == 'Open 24 hours') {
                $opn = ['open_time' => '00:00:00'];
                $cls = ['closed_time' => '00:00:00'];
            } else {
                $openclose = explode(' to ', $csv[$i][$config['food_opncls']]);
                $opn = ['open_time' => date("H:i:s", strtotime(trim($openclose[0], ' ')))];
                $cls = ['closed_time' => date("H:i:s", strtotime(trim($openclose[1], ' ')))];
            }
        }
        if(isset($FinalPath)) {
            $dataGallery = array_unique($FinalPath[$csv[$i][0]]);
            $countGallery = count($dataGallery);
        } else {
            $dataGallery = [];
            $countGallery = 0;
        }
        if(isset($MenuPath)) {
            $dataMenu = array_unique($MenuPath[$csv[$i][0]]['menu']);
            if(count($dataMenu) > 5) {
                $cutMenu = array_slice($dataMenu, 0, 5);
            } else {
                $cutMenu = $dataMenu;
            }
            foreach (array_unique($cutMenu) as $menu) {
                $files["menu_".$csv[$i][0]."_".$menu] = file_get_contents($menu);
            }
            $countMenu = count($cutMenu);
        } else {
            $dataMenu = [];
            $countMenu = 0;
        }
        if(isset($videosPath)) {
            $dataStory = array_unique($videosPath[$csv[$i][0]]['videos']);
            $countStory = count($dataStory);
        } else {
            $dataStory = [];
            $countStory = 0;
        }

        if(($countGallery + $countMenu + $countStory) > 15) {
            $getPhoto = preg_grep("/^.*\.(jpeg|jpg|png|webp)$/i", $dataGallery);
            $cutPhoto = array_slice($getPhoto, 0, 13);
            $getStory = preg_grep("/^.*\.(mp4|mov)$/i", $dataStory);
            if(!empty($getStory)) {
                $cutStory = array_slice($getStory, 0, 2);
                $arrayFiles = array_merge($cutPhoto, $cutStory);
            } else {
                $getGalleryStory = preg_grep("/^.*\.(mp4|mov)$/i", $dataGallery);
                if(!empty($getGalleryStory)) {
                    $cutStory = array_slice($getGalleryStory, 0, 2);
                    $arrayFiles = array_merge($cutPhoto, $cutStory);
                } else {
                    $arrayFiles = array_slice($getPhoto, 0, 15);
                }
            }
        } else {
            $arrayFiles = array_merge($dataGallery, $dataMenu, $dataStory);
        }

        foreach (array_unique($arrayFiles) as $file) {
            $files["gallery_".$csv[$i][0]."_".$file] = file_get_contents($file);
        }
        $textData = array_merge($name, $dec, $addr, $fac, $loc, $prc, $s_cat, $lat, $lon, $opn, $cls);

        if(is_null($textData)) {
            $cord = explode(', ', $csv[$i][$config['food_coordinate']]);
            if(!empty(trim($csv[$i][$config['food_opncls']], ' ')) && trim($csv[$i][$config['food_opncls']], ' ') !== 'Closed') {
                if(trim($csv[$i][$config['food_opncls']], ' ') == 'Open 24 hours') {
                    $opn = '00:00:00';
                    $cls = '00:00:00';
                } else {
                    $openclose = explode(' to ', $csv[$i][$config['food_opncls']]);
                    $opn = date("H:i:s", strtotime(trim($openclose[0], ' ')));
                    $cls = date("H:i:s", strtotime(trim($openclose[1], ' ')));
                }
            }

            $textData = [
                'name' => trim($csv[$i][$config['food_name']], ' '),
                'short_description' => trim($csv[$i][$config['food_sdesc']], ' '),
                'address' => trim($csv[$i][$config['food_address']], ' '),
                'phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['food_phone']]), ' '),
                'id_price' => strlen(trim($csv[$i][$config['food_price']], ' ')) == 3 ? 5 : strlen(trim($csv[$i][$config['food_price']], ' ')),
                'sub_cat' => trim(str_replace('restaurant', '', $csv[$i][$config['food_subcat']]), ' '),
                'facilities' => trim($csv[$i][$config['food_facilities']], ' ') ?? trim($csv[$i][$config['food_facilities2']], ' '),
                'location' => trim($csv[$i][$config['food_location']], ' '),
                'lat' => trim($cord[0], ' '),
                'lon' => trim($cord[1], ' '),
                'open_time' => $opn,
                'closed_time' => $cls
            ];
        }
    }
    if(isset($csv[$i][0]) !== 'title'  && $type == 'wow') {
        $name = $subcat = $dec = $addr = $loc = $phn = $web = $lat = $lon = $opn = $cls = [];
        if(!empty(trim($csv[$i][$config['wow_name']], ' '))) {
            $name = ['name' => trim($csv[$i][$config['wow_name']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_subcat']], ' '))) {
            $subcat = ['subcategory' => trim($csv[$i][$config['wow_subcat']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_sdesc']], ' '))) {
            $dec = ['short_description' => trim($csv[$i][$config['wow_sdesc']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_address']], ' '))) {
            $addr = ['address' => trim($csv[$i][$config['wow_address']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_phone']], ' '))) {
            $phn = ['phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['wow_phone']]), ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_website']], ' '))) {
            $web = ['website' => trim($csv[$i][$config['wow_website']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_facilities']]))) {
            $fac = ['facilities' => trim($csv[$i][$config['wow_facilities']], ' ')];
        } else {
            if(!empty(trim($csv[$i][$config['wow_facilities2']]))) {
                $fac = ['facilities' => trim($csv[$i][$config['wow_facilities2']], ' ')];
            }
        }
        if(!empty(trim($csv[$i][$config['wow_location']]))) {
            $loc = ['location' => trim($csv[$i][$config['wow_location']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_coordinate']], ' '))) {
            $cord = explode(', ', $csv[$i][$config['wow_coordinate']]);
            $lat = ['lat' => trim($cord[0], ' ')];
            $lon = ['lon' => trim($cord[1], ' ')];
        }
        if(!empty(trim($csv[$i][$config['wow_opncls']], ' ')) && trim($csv[$i][$config['wow_opncls']], ' ') !== 'Closed') {
            if(trim($csv[$i][$config['wow_opncls']], ' ') == 'Open 24 hours') {
                $opn = ['open_time' => '00:00:00'];
                $cls = ['closed_time' => '00:00:00'];
            } else {
                $openclose = explode(' to ', trim($csv[$i][$config['wow_opncls']], ' '));
                $opn = ['open_time' => date("H:i:s", strtotime(trim($openclose[0], ' ')))];
                $cls = ['closed_time' => date("H:i:s", strtotime(trim($openclose[1], ' ')))];
            }
        }
        if(isset($FinalPath)) {
            $dataGallery = array_unique($FinalPath[$csv[$i][0]]);
            $countGallery = count($dataGallery);
        } else {
            $dataGallery = [];
            $countGallery = 0;
        }
        if(isset($videosPath)) {
            $dataStory = array_unique($videosPath[$csv[$i][0]]['videos']);
            $countStory = count($dataStory);
        } else {
            $dataStory = [];
            $countStory = 0;
        }
        if(($countGallery + $countStory) > 20) {
            $getPhoto = preg_grep("/^.*\.(jpeg|jpg|png|webp)$/i", $dataGallery);
            $cutPhoto = array_slice($getPhoto, 0, 15);
            $getStory = preg_grep("/^.*\.(mp4|mov)$/i", $dataStory);
            if(!empty($getStory)) {
                $cutStory = array_slice($getStory, 0, 2);
                $arrayFiles = array_merge($cutPhoto, $cutStory);
            } else {
                $getGalleryStory = preg_grep("/^.*\.(mp4|mov)$/i", $dataGallery);
                if(!empty($getGalleryStory)) {
                    $cutStory = array_slice($getGalleryStory, 0, 2);
                    $arrayFiles = array_merge($cutPhoto, $cutStory);
                } else {
                    $arrayFiles = array_slice($getPhoto, 0, 20);
                }
            }
        } else {
            $arrayFiles = array_merge($dataGallery, $dataStory);
        }

        foreach (array_unique($arrayFiles) as $file) {
            $files[$file] = file_get_contents($file);
        }
        $textData = array_merge($name, $subcat, $dec, $addr, $loc, $fac, $phn, $web, $lat, $lon, $opn, $cls);

        if(is_null($textData)) {
            $cord = explode(', ', $csv[$i][$config['wow_coordinate']]);
            if(!empty(trim($csv[$i][$config['wow_opncls']], ' ')) && trim($csv[$i][$config['wow_opncls']], ' ') !== 'Closed') {
                if(trim($csv[$i][$config['wow_opncls']], ' ') == 'Open 24 hours') {
                    $opn = '00:00:00';
                    $cls = '00:00:00';
                } else {
                    $openclose = explode(' to ', trim($csv[$i][$config['wow_opncls']], ' '));
                    $opn = date("H:i:s", strtotime(trim($openclose[0], ' ')));
                    $cls = date("H:i:s", strtotime(trim($openclose[1], ' ')));
                }
            }

            $textData = [
                'name' => trim($csv[$i][$config['wow_name']], ' '),
                'short_description' => trim($csv[$i][$config['wow_sdesc']], ' '),
                'subcategory' => trim($csv[$i][$config['wow_subcat']], ' '),
                'address' => trim($csv[$i][$config['wow_address']], ' '),
                'facilities' => trim($csv[$i][$config['wow_facilities']], ' ') ?? trim($csv[$i][$config['wow_facilities2']], ' '),
                'phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['wow_phone']]), ' '),
                'website' => trim($csv[$i][$config['wow_website']], ' '),
                'location' => trim($csv[$i][$config['wow_location']], ' '),
                'lat' => trim($cord[0], ' '),
                'lon' => trim($cord[1], ' '),
                'open_time' => $opn,
                'closed_time' => $cls
            ];
        }
    }
    $boundary = uniqid();
    $delimiter = '-------------' . $boundary;
    $post_data = build_data_files($boundary, $textData, $files);
    $headers = ["Content-Type: multipart/form-data; boundary=" . $delimiter, "Content-Length: " . strlen($post_data)];
    $pool->add(new Process(
        $rollingCurl->setOptions([
            CURLOPT_HEADER => 0,
            CURLOPT_RETURNTRANSFER => 1,
            CURLOPT_SSL_VERIFYHOST => 0,
            CURLOPT_SSL_VERIFYPEER => 0,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_USERAGENT => base64_encode('EZV_Bot v1.1')
        ])->post($api_endpoint, $post_data)->setCallback(function(Request $request) {
            global $config, $i, $type, $csv;

            $status = json_decode($request->getResponseText(), true);
            if($status['status'] == 'success') {
                if((int)$config['delay'] > 0 && $i > 1) {
                    echo color("nevy","[EZVBOT] ❱❱ ".color('yellow', "Delay ({$config['delay']}) seconds...\n"));
                    sleep((int)$config['delay']);
                }
                if($type == 'villa') {
                    echo color("purple","[+]========[Success Add ({$i})]========[+]\n");
                    echo color("blue", format_string('[i] ID Villa', color("green", ": {$status['data']}")));
                    echo color("blue", format_string('[i] Name', color("green", ": {$status['name']}")));
                    echo color("blue", format_string('[i] Address', color("green", ": {$status['address']}")));
                    echo color("blue", format_string('[i] Latitude & Longitude', color("green", ": {$status['latitude']} / {$status['longitude']}")));
                    echo color("blue", format_string('[i] Url', color("green", ": {$config['url_villa']}{$status['data']}")));
                    echo color("blue", format_string('[i] Location', color("green", ": {$status['id_location']}")));
                    echo color("blue", format_string('[i] Gallery', color("green", ": {$status['gallery_photo']}")));
                    echo color("blue", format_string('[i] Story', color("green", ": {$status['story']}")));
                    echo color("blue", format_string('[i] Amenities', color("green", ": {$status['amenities']}")));
                    $logs = "[+]========[Success Add ({$i})]========[+]\n";
                    $logs .= "Time: {$status['time']}\n";
                    $logs .= "ID Villa: {$status['data']}\n";
                    $logs .= "Name: {$status['name']}\n";
                    $logs .= "Address: {$status['address']}\n";
                    $logs .= "Latitude & Longitude: {$status['latitude']} / {$status['longitude']}\n";
                    $logs .= "Url: {$config['url_villa']}{$status['data']}\n";
                    $logs .= "Location: {$status['id_location']}\n";
                    $logs .= "Gallery: {$status['gallery_photo']}\n";
                    $logs .= "Story: {$status['story']}\n";
                    $logs .= "Amenities: {$status['amenities']}\n";
                    file_put_contents('logs/villa_success_'.date('d-m-Y').'.log', $logs, FILE_APPEND | LOCK_EX);
                    // file_put_contents('csv/success-villa.csv', "{$i},\"{$csv[$i][1]}\",,,,\"{$csv[$i][5]}\",,,,,\"{$csv[1][$config['wow_phone']]}\",\"{$csv[$i][$config['wow_opncls']]}\",,\n", FILE_APPEND | LOCK_EX);
                }
                if($type == 'food') {
                    echo color("purple","[+]========[Success Add ({$i})]========[+]\n");
                    echo color("blue", format_string('[i] ID Restaurant', color("green", ": {$status['data']}")));
                    echo color("blue", format_string('[i] Name', color("green", ": {$status['name']}")));
                    echo color("blue", format_string('[i] Type', color("green", ": {$status['id_type']}")));
                    echo color("blue", format_string('[i] ID Price', color("green", ": {$status['id_price']}")));
                    echo color("blue", format_string('[i] Address', color("green", ": {$status['address']}")));
                    echo color("blue", format_string('[i] Facilities', color("green", ": {$status['facilities']}")));
                    echo color("blue", format_string('[i] Open - Close', color("green", ": {$status['open_close']}")));
                    echo color("blue", format_string('[i] Latitude & Longitude', color("green", ": {$status['latitude']} / {$status['longitude']}")));
                    echo color("blue", format_string('[i] Url', color("green", ": {$config['url_food']}{$status['data']}")));
                    echo color("blue", format_string('[i] Location', color("green", ": {$status['id_location']}")));
                    echo color("blue", format_string('[i] Short Description', color("green", ": {$status['short_description']}")));
                    echo color("blue", format_string('[i] Gallery', color("green", ": {$status['gallery_photo']}")));
                    echo color("blue", format_string('[i] Story', color("green", ": {$status['story']}")));
                    echo color("blue", format_string('[i] Menu', color("green", ": {$status['menu']}")));
                    $logs = "[+]========[Success Add ({$i})]========[+]\n";
                    $logs .= "Time: {$status['time']}\n";
                    $logs .= "ID Restaurant: {$status['data']}\n";
                    $logs .= "Name: {$status['name']}\n";
                    $logs .= "Type: {$status['id_type']}\n";
                    $logs .= "ID Price: {$status['id_price']}\n";
                    $logs .= "Address: {$status['address']}\n";
                    $logs .= "Facilities: {$status['facilities']}\n";
                    $logs .= "Open - Close: {$status['open_close']}\n";
                    $logs .= "Latitude & Longitude: {$status['latitude']} / {$status['longitude']}\n";
                    $logs .= "Url: {$config['url_food']}{$status['data']}\n";
                    $logs .= "Location: {$status['id_location']}\n";
                    $logs .= "Short Description: {$status['short_description']}\n";
                    $logs .= "Gallery: {$status['gallery_photo']}\n";
                    $logs .= "Story: {$status['story']}\n";
                    $logs .= "Menu: {$status['menu']}\n";
                    file_put_contents('logs/food_success_'.date('d-m-Y').'.log', $logs, FILE_APPEND | LOCK_EX);
                    // file_put_contents('csv/success-food.csv', "{$i},\"{$csv[$i][1]}\",,,\"{$csv[$i][$config['wow_address']]}\",\"{$csv[$i][5]}\",\"{$csv[$i][$config['wow_coordinate']]}\",,,\"{$csv[$i][$config['wow_website']]}\",,,,,,,,,\"{$csv[$i][18]}\",\"{$csv[$i][19]}\",\"{$csv[$i][20]}\",,\n", FILE_APPEND | LOCK_EX);
                }
                if($type == 'wow') {
                    echo color("purple","[+]========[Success Add ({$i})]========[+]\n");
                    echo color("blue", format_string('[i] ID Activity', color("green", ": {$status['data']}")));
                    echo color("blue", format_string('[i] Name', color("green", ": {$status['name']}")));
                    echo color("blue", format_string('[i] Sub Category', color("green", ": {$status['sub_category']}")));
                    echo color("blue", format_string('[i] Phone', color("green", ": {$status['phone']}")));
                    echo color("blue", format_string('[i] Website', color("green", ": {$status['website']}")));
                    echo color("blue", format_string('[i] Address', color("green", ": {$status['address']}")));
                    echo color("blue", format_string('[i] Facilities', color("green", ": {$status['facilities']}")));
                    echo color("blue", format_string('[i] Open - Close', color("green", ": {$status['open_close']}")));
                    echo color("blue", format_string('[i] Latitude & Longitude', color("green", ": {$status['latitude']} / {$status['longitude']}")));
                    echo color("blue", format_string('[i] Url', color("green", ": {$config['url_wow']}{$status['data']}")));
                    echo color("blue", format_string('[i] Location', color("green", ": {$status['id_location']}")));
                    echo color("blue", format_string('[i] Short Description', color("green", ": {$status['short_description']}")));
                    echo color("blue", format_string('[i] Gallery', color("green", ": {$status['gallery_photo']}")));
                    echo color("blue", format_string('[i] Story', color("green", ": {$status['story']}")));
                    $logs = "[+]========[Success Add ({$i})]========[+]\n";
                    $logs .= "Time: {$status['time']}\n";
                    $logs .= "ID Activity: {$status['data']}\n";
                    $logs .= "Name: {$status['name']}\n";
                    $logs .= "Sub Category: {$status['sub_category']}\n";
                    $logs .= "Phone: {$status['phone']}\n";
                    $logs .= "Website: {$status['website']}\n";
                    $logs .= "Address: {$status['address']}\n";
                    $logs .= "Facilities: {$status['facilities']}\n";
                    $logs .= "Open - Close: {$status['open_close']}\n";
                    $logs .= "Latitude & Longitude: {$status['latitude']} / {$status['longitude']}\n";
                    $logs .= "Url: {$config['url_wow']}{$status['data']}\n";
                    $logs .= "Location: {$status['id_location']}\n";
                    $logs .= "Short Description: {$status['short_description']}\n";
                    $logs .= "Gallery: {$status['gallery_photo']}\n";
                    $logs .= "Story: {$status['story']}\n";
                    file_put_contents('logs/wow_success_'.date('d-m-Y').'.log', $logs, FILE_APPEND | LOCK_EX);
                    // file_put_contents('csv/success-wow.csv', "{$i},\"{$csv[$i][1]}\",,,,\"{$csv[$i][5]}\",\"{$csv[$i][$config['wow_coordinate']]}\",,\"{$csv[$i][8]}\",\"{$csv[$i][$config['wow_website']]}\",\"{$csv[$i][$config['wow_phone']]}\",,\"{$csv[$i][12]}\",\"{$csv[$i][$config['wow_facilities']]}\",\n", FILE_APPEND | LOCK_EX);
                }
            } else {
                $error = $status['message'] ?? parseStr($request->getResponseText(), '<title>', '</title>');
                $sname = $status['name'] ?? $csv[$i][1];

                if(!empty($error)) {
                    echo color("purple","[!]========[Something wrong]========[!]\n");
                    echo color("red","[x] Error: {$error}\n");
                }

                if($type == 'villa') {
                    // file_put_contents('csv/error-villa.csv', "{$i},\"{$csv[$i][1]}\",,,,\"{$csv[$i][5]}\",,,,,\"{$csv[1][$config['wow_phone']]}\",\"{$csv[$i][$config['wow_opncls']]}\",,\n", FILE_APPEND | LOCK_EX);
                    file_put_contents('logs/villa_error_'.date('d-m-Y').'.log', "Villa: {$sname} ({$error})\n", FILE_APPEND | LOCK_EX);
                }
                if($type == 'food') {
                    // file_put_contents('csv/error-food.csv', "{$i},\"{$csv[$i][1]}\",,,\"{$csv[$i][$config['wow_address']]}\",\"{$csv[$i][5]}\",\"{$csv[$i][$config['wow_coordinate']]}\",,,\"{$csv[$i][$config['wow_website']]}\",,,,,,,,,\"{$csv[$i][18]}\",\"{$csv[$i][19]}\",\"{$csv[$i][20]}\",,\n", FILE_APPEND | LOCK_EX);
                    file_put_contents('logs/food_error_'.date('d-m-Y').'.log', "Restaurant: {$sname} ({$error})\n", FILE_APPEND | LOCK_EX);
                }
                if($type == 'wow') {
                    // file_put_contents('csv/error-wow.csv', "{$i},\"{$csv[$i][1]}\",,,,\"{$csv[$i][5]}\",\"{$csv[$i][$config['wow_coordinate']]}\",,\"{$csv[$i][8]}\",\"{$csv[$i][$config['wow_website']]}\",\"{$csv[$i][$config['wow_phone']]}\",,\"{$csv[$i][12]}\",\"{$csv[$i][$config['wow_facilities']]}\",\n", FILE_APPEND | LOCK_EX);
                    file_put_contents('logs/wow_error_'.date('d-m-Y').'.log', "Activity: {$sname} ({$error})\n", FILE_APPEND | LOCK_EX);
                }

            }
            if($config['debug_mode'] == 1) {
                if($type == 'villa') {
                    file_put_contents('logs/debug_villa.log', "=================================\nVilla ({$csv[$i][1]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                }
                if($type == 'food') {
                    file_put_contents('logs/debug_food.log', "=================================\nRestaurant ({$csv[$i][1]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                }
                if($type == 'wow') {
                    file_put_contents('logs/debug_wow.log', "=================================\nActivity ({$csv[$i][1]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                }
                file_put_contents('logs/debug_all.log', "=================================\n{$type} ({$csv[$i][1]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
            }
        })->setSimultaneousLimit((int)$amount_listing)->execute()
    ));
    showStatus($i, (int)$amount_listing, 38);
    if($i === (int)$amount_listing) {
        echo color("nevy","\n[EZVBOT] ❱❱ ".color('green', "Finish in " . (microtime(true) - $start) . " seconds\n\n"));
    }
    unset($files);
}
$pool->run();
