<?php
/*
████████████████████████████████████████████████████████████████████████████████████████████████████████
██                                                                                                    ██
██        _____   ______   __       __   ______   __              _______    ______   ________        ██
██       /     | /      \ /  \     /  | /      \ /  |            /       \  /      \ /        |       ██
██       $$$$$ |/$$$$$$  |$$  \   /$$ |/$$$$$$  |$$ |            $$$$$$$  |/$$$$$$  |$$$$$$$$/        ██
██          $$ |$$ |__$$ |$$$  \ /$$$ |$$ |__$$ |$$ |            $$ |__$$ |$$ |  $$ |   $$ |          ██
██     __   $$ |$$    $$ |$$$$  /$$$$ |$$    $$ |$$ |            $$    $$< $$ |  $$ |   $$ |          ██
██    /  |  $$ |$$$$$$$$ |$$ $$ $$/$$ |$$$$$$$$ |$$ |            $$$$$$$  |$$ |  $$ |   $$ |          ██
██    $$ \__$$ |$$ |  $$ |$$ |$$$/ $$ |$$ |  $$ |$$ |_____       $$ |__$$ |$$ \__$$ |   $$ |          ██
██    $$    $$/ $$ |  $$ |$$ | $/  $$ |$$ |  $$ |$$       |      $$    $$/ $$    $$/    $$ |          ██
██     $$$$$$/  $$/   $$/ $$/      $$/ $$/   $$/ $$$$$$$$/       $$$$$$$/   $$$$$$/     $$/   V4.0    ██
██                                                                                                    ██
██    Coded By: Jamal Bigballs                                                                        ██
██    Author URI: https://www.jamal-bigballs.dev/                                                     ██
██    License: GNU General Public License v2 or later                                                 ██
██    License URI: http://www.gnu.org/licenses/gpl-2.0.html                                           ██
██                                                                                                    ██
████████████████████████████████████████████████████████████████████████████████████████████████████████

    "Keep on Never Tired of Learning"
    Jamal Bigball est.2022
*/
ini_set("memory_limit", "-1");
set_time_limit(0);
error_reporting(0);

require_once 'modules/Curl.php';
require_once 'modules/Functions.php';
require_once 'modules/Telegram.php';
require_once 'vendor/autoload.php';

use Graze\ParallelProcess\Pool;
use Symfony\Component\Process\Process;

$telegram = new Telegram('6055166918:AAFhXwXfAuQtfYT2UnCLjqJQLGVkq2s37P8');
$config = parse_ini_file("config.ini");
$CurlClass = new Curl();

echo cover();
// bruh:
// echo color("nevy",'[+] ').color("purple","=================================").color("nevy",' [+]')."\n";
// foreach (["villa", "food", "wow", "hotel"] as $key => $value) {
//     $typeList[] = $value;
//     echo color("nevy",'[i] ').color('blue' , trim(format_string($value, "[$key]")))."\n";
// }
// echo color("nevy",'[+] ').color("purple","=================================").color("nevy",' [+]')."\n\n";
// $typ = stuck("Enter the listing type number : ");

// if($typ  == '') {
//     echo "\n";
//     echo color("nevy","[JAMALBOT] ❱❱ ".color('red', "User cancelled process\n"));
//     die();
// }
// $type = $typeList[$typ];
$type = $config['type'];
if(!in_array($type, ["villa", "food", "wow", "hotel"])) {
    echo color("nevy","[JAMALBOT] ❱❱ ".color('red', "Invalid data bruhh...\n"));
    die();
    // goto bruh;
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
    case 'hotel':
        $api_endpoint = $config['api'].$config['hotel'];
        break;
    default:
        $api_endpoint = $config['api'].$config['villa'];
        break;
}

echo color("nevy","[JAMALBOT] ❱❱ ".color('purple', "Looking for an csv file...\n"));

$locdir_list = $config['dir_scraping'];
$csvpath = $locdir_list.$config['dir_csv'].$config['csv'];

if(!file_exists($csvpath)) {
    echo color("nevy","[JAMALBOT] ❱❱ ".color('red', "CSV files not found!\n"));
    die();
}
$media_load = scandir($locdir_list.'/image_gallery');
foreach($media_load as $folder) {
    if($folder !== '.' && $folder !== '..') {
        $mediaList = scandir($locdir_list.'/image_gallery/'.$folder);
        foreach($mediaList as $media) {
            if($media !== '.' && $media !== '..') {
                if(is_file($locdir_list.'/image_gallery/'.$folder.'/'.$media)) {
                    $FinalPath[$folder][] = $locdir_list.'/image_gallery/'.$folder.'/'.$media;
                } else {
                    if(is_dir($locdir_list.'/image_gallery/'.$folder.'/menu')) {
                        $menuList = scandir($locdir_list.'/image_gallery/'.$folder.'/menu');
                        foreach($menuList as $menu) {
                            if($menu !== '.' && $menu !== '..') {
                                if(is_file($locdir_list.'/image_gallery/'.$folder.'/menu/'.$menu)) {
                                    $MenuPath[$folder]['menu'][] = $locdir_list.'/image_gallery/'.$folder.'/menu/'.$menu;
                                }
                            }
                        }
                    }
                    if(is_dir($locdir_list.'/image_gallery/'.$folder.'/videos')) {
                        $videosList = scandir($locdir_list.'/image_gallery/'.$folder.'/videos');
                        foreach($videosList as $videos) {
                            if($videos !== '.' && $videos !== '..') {
                                if(is_file($locdir_list.'/image_gallery/'.$folder.'/videos/'.$videos)) {
                                    $videosPath[$folder]['videos'][] = $locdir_list.'/image_gallery/'.$folder.'/videos/'.$videos;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

$csv = array_filter(csvToArray($csvpath));

$amount_listing = count($csv) - 1;

echo color("nevy","[JAMALBOT] ❱❱ ".color('blue', "Listing to add: {$amount_listing} data\n"));
$start = microtime(true);
echo color("nevy","[JAMALBOT] ❱❱ ".color('green', "Starting process...\n\n"));

$pool = new Pool();
$added = $exsts = $nogal = $err = $toterr = 0;

for ($i = 1; $i <= (int)$amount_listing; $i++) {
    if(isset($csv[$i][0]) !== 'title' && $type == 'villa') {
        $name = $addr = $loc = $phn = $fac = $lat = $lon = [];
        $check_status = json_decode(check_status(trim($csv[$i][$config['villa_name']], ' '), $type), true);
        if($check_status['status'] == 'Error') {
            echo color("purple","[!]========[Something wrong ({$i})]========[!]\n");
            echo color("red","[x] Error: {$check_status['message']}\n");
            $exists = true;
            goto exixts;
        }
        if($check_status['status'] == 'success') {
            $exists = false;
        }
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
                'facilities' => trim($csv[$i][$config['villa_facilities']], ' '),
                'location' => trim($csv[$i][$config['villa_location']], ' '),
                'lat' => trim($cord[0], ' '),
                'lon' => trim($cord[1], ' ')
            ];
        }
    }
    if(isset($csv[$i][0]) !== 'title'  && $type == 'food') {
        $name = $dec = $addr = $phn = $loc = $prc = $s_cat = $lat = $lon = $opn = $cls = [];
        $check_status = json_decode(check_status(trim($csv[$i][$config['food_name']], ' '), $type), true);
        if($check_status['status'] == 'Error') {
            echo color("purple","[!]========[Something wrong ({$i})]========[!]\n");
            echo color("red","[x] Error: {$check_status['message']}\n");
            $exists = true;
            goto exixts;
        }
        if($check_status['status'] == 'success') {
            $exists = false;
        }
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
                'facilities' => trim($csv[$i][$config['food_facilities']], ' '),
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
        $check_status = json_decode(check_status(trim($csv[$i][$config['wow_name']], ' '), $type), true);
        if($check_status['status'] == 'Error') {
            echo color("purple","[!]========[Something wrong ({$i})]========[!]\n");
            echo color("red","[x] Error: {$check_status['message']}\n");
            $exists = true;
            goto exixts;
        }
        if($check_status['status'] == 'success') {
            $exists = false;
        }
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
                'facilities' => trim($csv[$i][$config['wow_facilities']], ' '),
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
    if(isset($csv[$i][0]) !== 'title'  && $type == 'hotel') {
        $name = $dec = $addr = $loc = $phn = $lat = $lon = [];
        $check_status = json_decode(check_status(trim($csv[$i][$config['hotel_name']], ' '), $type), true);
        if($check_status['status'] == 'Error') {
            echo color("purple","[!]========[Something wrong ({$i})]========[!]\n");
            echo color("red","[x] Error: {$check_status['message']}\n");
            $exists = true;
            goto exixts;
        }
        if($check_status['status'] == 'success') {
            $exists = false;
        }
        if(!empty(trim($csv[$i][$config['hotel_name']], ' '))) {
            $name = ['name' => trim($csv[$i][$config['hotel_name']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['hotel_sdesc']], ' '))) {
            $dec = ['short_description' => trim($csv[$i][$config['hotel_sdesc']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['hotel_address']], ' '))) {
            $addr = ['address' => trim($csv[$i][$config['hotel_address']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['hotel_phone']], ' '))) {
            $phn = ['phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['hotel_phone']]), ' ')];
        }
        if(!empty(trim($csv[$i][$config['hotel_facilities']]))) {
            $fac = ['facilities' => trim($csv[$i][$config['hotel_facilities']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['hotel_location']]))) {
            $loc = ['location' => trim($csv[$i][$config['hotel_location']], ' ')];
        }
        if(!empty(trim($csv[$i][$config['hotel_coordinate']], ' '))) {
            $cord = explode(', ', $csv[$i][$config['hotel_coordinate']]);
            $lat = ['lat' => trim($cord[0], ' ')];
            $lon = ['lon' => trim($cord[1], ' ')];
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
        $textData = array_merge($name, $dec, $addr, $loc, $fac, $phn, $lat, $lon);

        if(is_null($textData)) {
            $cord = explode(', ', $csv[$i][$config['hotel_coordinate']]);

            $textData = [
                'name' => trim($csv[$i][$config['hotel_name']], ' '),
                'short_description' => trim($csv[$i][$config['hotel_sdesc']], ' '),
                'address' => trim($csv[$i][$config['hotel_address']], ' '),
                'facilities' => trim($csv[$i][$config['hotel_facilities']], ' '),
                'phone' => trim(str_replace('phone:tel:', '', $csv[$i][$config['hotel_phone']]), ' '),
                'location' => trim($csv[$i][$config['hotel_location']], ' '),
                'lat' => trim($cord[0], ' '),
                'lon' => trim($cord[1], ' ')
            ];
        }
    }
    exixts:
    if($exists) {
        showStatus($i, (int)$amount_listing, 38);
        if($i === (int)$amount_listing) {
            $text = "#=======Report Bot=======#\n";
            $text .= "Date : ".date('d-m-Y H:i:s')."\n";
            $text .= "Type : {$type}\n";
            $text .= "Success : {$added}\n";
            $text .= "Exists : {$exsts}\n";
            $text .= "No gallery : {$nogal}\n";
            $text .= "Error : {$err}\n";
            $text .= "Total : {$amount_listing}\n";
            $text .= "Time elapsed : " . number_format(microtime(true) - $start) . " seconds\n";
            $text .= "#========================#\n\n";

            $content = array('chat_id' => $config['admin_tele'], 'text' => $text);
            $telegram->sendMessage($content);

            echo color("nevy","\n[JAMALBOT] ❱❱ ".color('nevy', "Success Add: ({$added}) data | Error Add: ({$toterr}) data\n\n"));
            echo color("nevy","\n[JAMALBOT] ❱❱ ".color('green', "Finish in " . number_format(microtime(true) - $start) . " seconds\n\n"));
        }
        unset($files);
        continue;
    } else {
        $boundary = uniqid();
        $delimiter = '-------------' . $boundary;
        $post_data = build_data_files($boundary, $textData, $files);
        $pool->add(new Process(
            $CurlClass->setOptions([
                CURLOPT_HEADER => 0,
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_SSL_VERIFYHOST => 0,
                CURLOPT_SSL_VERIFYPEER => 0,
                CURLOPT_HTTPHEADER => ["Content-Type: multipart/form-data; boundary=" . $delimiter, "Content-Length: " . strlen($post_data)],
                CURLOPT_USERAGENT => base64_encode('JAMAL_Bot v4.0')
            ])->post($api_endpoint, $post_data)->setCallback(function(Request $request) {
                global $config, $i, $type, $csv, $added, $exsts, $nogal, $err, $toterr;

                $status = json_decode($request->getResponseText(), true);
                if($status['status'] == 'success') {
                    if((int)$config['delay'] > 0 && $i > 1) {
                        echo color("nevy","[JAMALBOT] ❱❱ ".color('yellow', "Delay ({$config['delay']}) seconds...\n"));
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
                    if($type == 'hotel') {
                        echo color("purple","[+]========[Success Add ({$i})]========[+]\n");
                        echo color("blue", format_string('[i] ID Hotel', color("green", ": {$status['data']}")));
                        echo color("blue", format_string('[i] Name', color("green", ": {$status['name']}")));
                        echo color("blue", format_string('[i] Phone', color("green", ": {$status['phone']}")));
                        echo color("blue", format_string('[i] Address', color("green", ": {$status['address']}")));
                        // echo color("blue", format_string('[i] Facilities', color("green", ": {$status['facilities']}")));
                        echo color("blue", format_string('[i] Latitude & Longitude', color("green", ": {$status['latitude']} / {$status['longitude']}")));
                        echo color("blue", format_string('[i] Url', color("green", ": {$config['url_hotel']}{$status['data']}")));
                        echo color("blue", format_string('[i] Location', color("green", ": {$status['id_location']}")));
                        echo color("blue", format_string('[i] Short Description', color("green", ": {$status['short_description']}")));
                        echo color("blue", format_string('[i] Gallery', color("green", ": {$status['gallery_photo']}")));
                        echo color("blue", format_string('[i] Story', color("green", ": {$status['story']}")));
                        $logs = "[+]========[Success Add ({$i})]========[+]\n";
                        $logs .= "Time: {$status['time']}\n";
                        $logs .= "ID Hotel: {$status['data']}\n";
                        $logs .= "Name: {$status['name']}\n";
                        $logs .= "Phone: {$status['phone']}\n";
                        $logs .= "Address: {$status['address']}\n";
                        // $logs .= "Facilities: {$status['facilities']}\n";
                        $logs .= "Latitude & Longitude: {$status['latitude']} / {$status['longitude']}\n";
                        $logs .= "Url: {$config['url_wow']}{$status['data']}\n";
                        $logs .= "Location: {$status['id_location']}\n";
                        $logs .= "Short Description: {$status['short_description']}\n";
                        $logs .= "Gallery: {$status['gallery_photo']}\n";
                        $logs .= "Story: {$status['story']}\n";
                        file_put_contents('logs/hotel_success_'.date('d-m-Y').'.log', $logs, FILE_APPEND | LOCK_EX);
                    }
                    $added = $added + 1;
                } else {
                    $error = $status['message'] ?? parseStr($request->getResponseText(), '<title>', '</title>');
                    $sname = $status['name'] ?? $csv[$i][1];

                    if(!empty($error)) {
                        echo color("purple","[!]========[Something wrong]========[!]\n");
                        echo color("red","[x] Error: {$error}\n");
                    }

                    if($type == 'villa') {
                        file_put_contents('csv/error-villa.csv', "\"{$csv[$i][$config['villa_name']]}\",\"{$csv[$i][$config['villa_address']]}\",\"{$csv[$i][$config['villa_phone']]}\",\"{$csv[$i][$config['villa_facilities']]}\",\"{$csv[$i][$config['villa_coordinate']]}\",\"{$csv[$i][$config['villa_location']]}\"\n", FILE_APPEND | LOCK_EX);
                        file_put_contents('logs/villa_error_'.date('d-m-Y').'.log', "Villa: {$sname} ({$error})\n", FILE_APPEND | LOCK_EX);
                    }
                    if($type == 'food') {
                        file_put_contents('csv/error-food.csv', "\"{$csv[$i][$config['food_name']]}\",\"{$csv[$i][$config['food_sdesc']]}\",\"{$csv[$i][$config['food_address']]}\",\"{$csv[$i][$config['food_phone']]}\",\"{$csv[$i][$config['food_price']]}\",\"{$csv[$i][$config['food_subcat']]}\",\"{$csv[$i][$config['food_facilities']]}\",\"{$csv[$i][$config['food_location']]}\",\"{$csv[$i][$config['food_coordinate']]}\",\"{$csv[$i][$config['food_opncls']]}\"\n", FILE_APPEND | LOCK_EX);
                        file_put_contents('logs/food_error_'.date('d-m-Y').'.log', "Restaurant: {$sname} ({$error})\n", FILE_APPEND | LOCK_EX);
                    }
                    if($type == 'wow') {
                        file_put_contents('csv/error-wow.csv', "\"{$csv[$i][$config['wow_name']]}\",\"{$csv[$i][$config['wow_subcat']]}\",\"{$csv[$i][$config['wow_sdesc']]}\",\"{$csv[$i][$config['wow_address']]}\",\"{$csv[$i][$config['wow_phone']]}\",\"{$csv[$i][$config['wow_website']]}\",\"{$csv[$i][$config['wow_facilities']]}\",\"{$csv[$i][$config['wow_location']]}\",\"{$csv[$i][$config['wow_coordinate']]}\",\"{$csv[$i][$config['wow_opncls']]}\"\n", FILE_APPEND | LOCK_EX);
                        file_put_contents('logs/wow_error_'.date('d-m-Y').'.log', "Activity: {$sname} ({$error})\n", FILE_APPEND | LOCK_EX);
                    }
                    if($type == 'hotel') {
                        file_put_contents('logs/hotel_error_'.date('d-m-Y').'.log', "Hotel: {$sname} ({$error})\n", FILE_APPEND | LOCK_EX);
                    }
                    if(preg_match("/already exists/", $status['message'])) {
                        $exsts = $exsts + 1;
                    } else if(preg_match("/no gallery/", $status['message'])) {
                        $nogal = $nogal + 1;
                    } else {
                        $err = $err + 1;
                    }
                    $toterr = $toterr + 1;
                }
                if($config['debug_mode'] == 1) {
                    if($type == 'villa') {
                        file_put_contents('logs/debug_villa.log', "=================================\nVilla ({$csv[$i][$config['villa_name']]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                    }
                    if($type == 'food') {
                        file_put_contents('logs/debug_food.log', "=================================\nRestaurant ({$csv[$i][$config['food_name']]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                    }
                    if($type == 'wow') {
                        file_put_contents('logs/debug_wow.log', "=================================\nActivity ({$csv[$i][$config['wow_name']]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                    }
                    if($type == 'hotel') {
                        file_put_contents('logs/debug_hotel.log', "=================================\nHotel ({$csv[$i][$config['hotel_name']]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                    }
                    file_put_contents('logs/debug_all.log', "=================================\n{$type} ({$csv[$i][0]}): ".$request->getResponseText()."\n", FILE_APPEND | LOCK_EX);
                }
            })->setSimultaneousLimit((int)$amount_listing)->execute()
        ));
        showStatus($i, (int)$amount_listing, 38);
        if($i === (int)$amount_listing) {
            $text = "#=======Report Bot=======#\n";
            $text .= "Date : ".date('d-m-Y H:i:s')."\n";
            $text .= "Type : {$type}\n";
            $text .= "Success : {$added}\n";
            $text .= "Exists : {$exsts}\n";
            $text .= "No gallery : {$nogal}\n";
            $text .= "Error : {$err}\n";
            $text .= "Total : {$amount_listing}\n";
            $text .= "Time elapsed : " . number_format(microtime(true) - $start) . " seconds\n";
            $text .= "#========================#\n\n";

            $content = array('chat_id' => $config['admin_tele'], 'text' => $text);
            $telegram->sendMessage($content);

            echo color("nevy","\n[JAMALBOT] ❱❱ ".color('nevy', "Success Add: ({$added}) data | Error Add: ({$toterr}) data\n\n"));
            echo color("nevy","\n[JAMALBOT] ❱❱ ".color('green', "Finish in " . number_format(microtime(true) - $start) . " seconds\n\n"));
        }
        unset($files);
    }
}
$pool->run();
