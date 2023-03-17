<?php

function check($name, $type) {
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

$test = check('Villa Cordoba', 'villa');
var_dump($test);
