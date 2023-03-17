<?php
function csvToArray($csvFile){
    $file_to_read = fopen($csvFile, 'r');
    while (!feof($file_to_read) ) {
        $lines[] = fgetcsv($file_to_read, 1000, ',');
    }
    fclose($file_to_read);
    return $lines;
}
function getLatLngFromGoogle($address) {
    $API_KEY = "AIzaSyCJyDp4TLGUigRfo4YN46dXcWOPRqLD0gQ";
    $url = "https://maps.google.com/maps/api/geocode/json?address=".urlencode($address)."&sensor=false&region=bali&key=".$API_KEY;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
    $response = curl_exec($ch);
    curl_close($ch);
    $returnBody = json_decode($response);

    $status = $returnBody->status;
    if($status == "REQUEST_DENIED"){
        $data['error'] = $returnBody->error_message;
    } else {
        $data['lat'] = $returnBody->results[0]->geometry->location->lat;
        $data['lng'] = $returnBody->results[0]->geometry->location->lng;
    }
    return $data;
}
function gratisan($addr) {
    $curl = curl_init('https://us1.locationiq.com/v1/search?key=pk.439605fe6e94cf67f81e1934e4bde486&q='.urlencode($addr).'&limit=1&matchquality=1&addressdetails=1&countrycodes=id&format=json');

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
      return json_decode($response, true);
    }
}
$csvFile = 'csv/master_hotel.csv';
$csv = csvToArray($csvFile);
// var_dump(gratisan('Jl. Kayu Jati No.1'));
// echo strlen('$$$');
// var_dump($csv);
$dir = 'csv/media';
$list_load = scandir($dir);
foreach($list_load as $folder) {
    if($folder !== '.' && $folder !== '..') {
        $mediaList = scandir($dir.'/'.$folder);
        foreach($mediaList as $media) {
            if($media !== '.' && $media !== '..') {
                if(is_file($dir.'/'.$folder.'/'.$media)) {
                    $FinalPath[$folder][] = $dir.'/'.$folder.'/'.$media;
                } else {
                    if(is_dir($dir.'/'.$folder.'/menu')) {
                        $menuList = scandir($dir.'/'.$folder.'/menu');
                        foreach($menuList as $menu) {
                            if($menu !== '.' && $menu !== '..') {
                                if(is_file($dir.'/'.$folder.'/menu/'.$menu)) {
                                    $MenuPath[$folder]['menu'][] = $dir.'/'.$folder.'/menu/'.$menu;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
// $getPhoto = preg_grep ("/^.*\.(jpeg|jpg|png|webp)$/i", $FinalPath['Abunawas Restaurant Bali']);
// $cutPhoto = array_slice($getPhoto, 0, 19);
// $getStory = preg_grep ("/^.*\.(mp4|mov)$/i", $FinalPath['Abunawas Restaurant Bali']);
// $cutStory = array_slice($getStory, 0, 2);
// $arrayFiles = array_merge($cutPhoto, $cutStory);
// $dir = 'csv/media';
// $folder = 'Sisterfields';

// if(is_dir($dir.'/'.$folder.'/menu')) {
//     $menuList = scandir($dir.'/'.$folder.'/menu');
//     foreach($menuList as $menu) {
//         if($menu !== '.' && $menu !== '..') {
//             if(is_file($dir.'/'.$folder.'/menu/'.$menu)) {
//                 $MenuPath[$folder]['menu'][] = $dir.'/'.$folder.'/menu/'.$menu;
//             }
//         }
//     }
// }
// var_dump(array_unique($MenuPath[$csv[1][1]]['menu']));
// var_dump($FinalPath[$csv[1][1]]);

// $data = explode(' to ', $csv[1][18]);
// $expldFac = explode(' | ', $csv[14][8]);

var_dump($csv);
// $data = $csv[1][18]
// echo date("H:i:s", strtotime($data[1]));

// $cord = explode(', ', $csv[1][19]);
// var_dump($cord);
// for ($i = 1; $i <= 100; $i++) {
//     if(!empty($csv[$i][14]) && $csv[$i][14] !== 'Amenities') {
//         var_dump($csv[$i]);
//     }

// }
// echo implode(',', $csv[0]);
// $fclts = trim($csv[1][14], ' ');
// $serialized = serialize($fclts);
// $myNewArray = unserialize($serialized);
// var_dump(json_decode($fclts, true));
?>
