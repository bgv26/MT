<?php
$start = microtime(true);
header('Content-type: text/xml;  charset:UTF-8; ');

echo "+-------------------------------------------------------------+\n";
echo "|                     " . date('d.m.Y H:i:s') . "                    |\n";
echo "+-------------------------------------------------------------+\n";
echo "v 1.02\n";

//Поиск слов в тексте
function strposa($haystack, $needle, $offset = 0)
{
    if (!is_array($needle)) $needle = array($needle);
    foreach ($needle as $query) {
        //if(strpos($haystack, $query, $offset) !== false) return true; // stop on first true result
        if (mb_strpos($haystack, $query, $offset) !== false) {
            echo "\n" . 'Found block text ! Position:' . strpos($haystack, $query, $offset) . '; String:' . $query . "\n";
            return true; // stop on first true result
        }
    }
    //return false;
    return false;
}

//Размер файла
function size($path)
{
    $bytes = sprintf('%u', filesize($path));
    if ($bytes > 0) {
        $unit = intval(log($bytes, 1024));
        $units = array('B', 'KB', 'MB', 'GB');
        if (array_key_exists($unit, $units) === true) {
            return sprintf('%d %s', $bytes / pow(1024, $unit), $units[$unit]);
        }
    }
    return $bytes;
}

//Добавляем SimpleXML строку в SimpleXML объект
function sxml_append(SimpleXMLElement $to, SimpleXMLElement $from)
{
    $toDom = dom_import_simplexml($to);
    $fromDom = dom_import_simplexml($from);
    $toDom->appendChild($toDom->ownerDocument->importNode($fromDom, true));
}

//Добавляем SimpleXML строку в SimpleXML объект
function sxml_append1(SimpleXMLElement $to, $tmp_string)
{
    $toDom = dom_import_simplexml($to);
    $fromDom = dom_import_simplexml(simplexml_load_string($tmp_string));
    $toDom->appendChild($toDom->ownerDocument->importNode($fromDom, true));
}

//Добавляем SimpleXML строку в SimpleXML объект
function sxml_append2(SimpleXMLElement $to, $tmp_string)
{
    $yesterday_str = date('Y-m-d', time() - 60 * 60 * 24);
    $today_str = date('Y-m-d');
    $tomorrow_str = date('Y-m-d', time() + 60 * 60 * 24);
    $hour = date('H');
    if ($hour >= '15' && $hour <= '17') {
        $tmp_string = preg_replace('/<DateBegin>([\d-]{10})<\/DateBegin>/', "<DateBegin>" . $tomorrow_str . "</DateBegin>", $tmp_string);
        $tmp_string = preg_replace('/<DateEnd>([\d-]{10})<\/DateEnd>/', "<DateEnd>" . $tomorrow_str . "</DateEnd>", $tmp_string);
    } else {
        $tmp_string = preg_replace('/<DateBegin>([\d-]{10})<\/DateBegin>/', "<DateBegin>" . $today_str . "</DateBegin>", $tmp_string);
        $tmp_string = preg_replace('/<DateEnd>([\d-]{10})<\/DateEnd>/', "<DateEnd>" . $today_str . "</DateEnd>", $tmp_string);
    }
    $toDom = dom_import_simplexml($to);
    $fromDom = dom_import_simplexml(simplexml_load_string($tmp_string));
    $toDom->appendChild($toDom->ownerDocument->importNode($fromDom, true));
}

//*/

/*
 *  Get catalog.txt
 */

$local_file = '/home/xml/temp/catalog.txt';
//$local_file = './catalog2.txt';

//*
if (file_exists($local_file)) {
    echo "Found ($local_file file) ... Ok.\n";
    echo "File date: [" . date("d.m.Y H:i:s.", fileatime($local_file)) . "]\n";
    echo "File size: [" . size($local_file) . "]\n";
} else {
    echo "\nWARNING. Can't loading  ($local_file)\n";

    //Соединяемся с ftp и забираем выгрузку на сайт в виде catalog.txt
    //$ftp_server = "37.230.113.141";
    //$ftp_server = "176.9.4.154";
    $ftp_server = "136.243.74.77";
    $conn_id = ftp_connect($ftp_server)
    or die("\nERROR. Couldn't connect to ($ftp_server)\n");
    echo "Connecting to ftp ... Ok.\n";
    $login_result = ftp_login($conn_id, "donmtmain", "QpTGdXal");
    if ((!$conn_id) || (!$login_result))
        die("\nERROR. FTP Connection Failed\n");
    echo "Login to ftp ... Ok.\n";
    $server_file = '/catalog/catalog.txt';
    echo "Copy file ($server_file) from ftp to ($local_file) ...";
    // попытка скачать $server_file и сохранить в $local_file
    if (ftp_get($conn_id, $local_file, $server_file, FTP_BINARY)) {
        echo "Ok.\n";
        echo "File $local_file modification time: " . date("F d Y H:i:s.", fileatime($local_file)) . "\n";
    } else {
        echo "\nERROR. Can't copy file ftp://$ftp_server$server_file \n";
    }
    ftp_close($conn_id);
}
//*/ 

$offices_ag_num = array(
    '7' => 'офис Батайский',
    '9' => 'офис Восточный',
    '2' => 'офис Западный',
    '4' => 'офис Королева',
    '5' => 'офис Добровольского',
    '8' => 'офис Стройгородок',
    '6' => 'офис Темерницкая',
    '3' => 'офис Социалистическая',
    '1' => 'офис Буденовский',
);

$file_name = glob($local_file);
$file_name = @$file_name[0];
$i = 0;
$j = 0;
$count = 0;
//$rows = array();
//echo "Get all agents ID from ($local_file) file ...\n";
//fwrite($tmp_log, "\nGet all agent [$agent_id] ID's' catalog file ...\n\n");
//Обработка файла catalog.txt
$agent_array = array();
$lot_array = array();
$rnd_array = array();
$est_array = array();
if (is_readable($file_name) && $tmp_file = @fopen($file_name, 'r')) {
    while (!feof($tmp_file)) {
        $file_line = fgets($tmp_file);
        if ($j > 0) {
            $file_line = iconv('Windows-1251', 'UTF-8', $file_line);
            $file_line = str_replace('"', '', $file_line);
            //$file_line = iconv ('CP866', 'UTF-8', $file_line);
            //$file_line = str_replace('; ','|',$file_line);
            //$file_line = str_replace('  ',' ',$file_line);
            $file_line = explode("\t", $file_line);
            if (is_array($file_line))
                if (isset($file_line[99]) && isset($file_line[94]) && isset($file_line[61]) && isset($file_line[58]))
                    if ($file_line[99] != "" && $file_line[94] != "" && $file_line[61] != "" && $file_line[58] != "") {
                        /*
                        $prefix = substr( $file_line[99], 2, 2);
                        if ($prefix == '11' ) {
                         $id = "1103" . substr( $file_line[99], 4, 8);
                        } elseif ( $prefix == '12' ) {
                         $id = "1203" . substr( $file_line[99], 4, 8);
                        } else {
                         $id = "Error";
                        }
                        */
                        /*
                        $offices_num = array_search ($file_line[58], $offices_ag_num);
                        //$agent_array[$offices_num][$id][] = $file_line['94'];
                        $lot_array[$offices_num][] = $file_line['6'];
                        //$lot_array[$offices_num][] = $id;
                        //$est_array[$offices_num][] = trim($file_line['2']) . '|' . trim($file_line['4']);
                        //$rnd_array[$offices_num][] = get_sum(strtr($file_line['6'], $offices_char_code));
                        $date_array[$offices_num][] = $file_line['61'];
                        //*/
                        $lot_array[] = $file_line['6'];
                        $date_array[] = $file_line['61'];
                    }
        }
        $j++;
    }
    echo "Ok.\n";
    fclose($tmp_file);
} else {
    echo "\nERROR. Can't loading ($file_name) !\n";
    exit(3);
}
echo "Loading " . $j . " lots from " . $file_name . "\n";

//FULL LOG
/*
echo 'Lots:'.print_r($lot_array,1)."\n";
*/

//echo '<pre>'.print_r($lot_array,1).'</pre>';
/*
$log_file = './offices_'.date('Y.m.d__H.i').'.log';
echo "Open ($log_file file) ...";
if ( $tmp_log = @fopen($log_file, 'w+') ) {
 //fclose($tmp_log);
 fwrite($tmp_log, "\n------------------------------\n");
 fwrite($tmp_log, "       " . date('Y.m.d   H:i:s') );
 fwrite($tmp_log, "\n------------------------------\n");
 echo " Ok.\n";
} else {
 die("\nERROR. Can't open log file.\n");
}
//Пишем в лог и закрываем.

fwrite($tmp_log, print_r($lot_array,1));
fwrite($tmp_log, print_r($date_array,1));
//*/
//*
//fwrite($tmp_log, "------------------------------\n");
//fwrite($tmp_log, "------------------------------\n");
//fclose($tmp_log);
//*/

$districts = array(
    1 => 'Ворошиловский',
    2 => 'Железнодорожный',
    3 => 'Кировский',
    4 => 'Ленинский',
    5 => 'Октябрьский',
    6 => 'Первомайский',
    7 => 'Пролетарский',
    8 => 'Советский'
);
/*
 $materials = array (
  'кирпич' => 'Кирпич',
  'панель' => 'Современная панель',
  'монолит' => 'Монолит',
  'другое' => 'Остальные'
  );
*/

$materials = array(
    'кирпичный' => 'Кирпич',
    'панельный' => 'Современная панель',
    'монолит' => 'Монолит',
    //'другое' => 'Остальные'
);

$places_bat = array(
    'Батайск' => 'Батайск',
    //'Авиагородок Микрорайон' => 'Авиагородок',
    'Батайск*' => 'Авиагородок',
    'Батайск**' => 'ВЖМ',
    'Батайск***' => 'Гайдара',
    //'Дачный Переулок' => 'Дачный',
    'Батайск****' => 'Дачный',
    //'Залесье' => 'Залесье',
    'Батайск*****' => 'Залесье',
    'Батайск******' => 'Западный Батайск',
    'Батайск*******' => 'Заря',
    'Батайск********' => 'Красный сад',
    'Батайск*********' => 'Наливная',
    'Батайск**********' => 'РДВС',
    'Батайск***********' => 'Соленое озеро',
    'Батайск************' => 'Солнечный',
    'Батайск*************' => 'Старый город',
    'Батайск*************' => 'Старый город',
    'Батайск**************' => 'Стадионный',
    //'Коваливского' => 'Коваливского',
    'Залесье' => 'Залесье/Остановка',
    'Лунева' => 'Лунева',
    'Булгакова' => 'Булгакова',
    'Локомотивный' => 'Локомотивный',
    //'Красный сад' => 'Лунева',
    //'Батайск**************' => 'Половинко',
    'Крупской' => 'Крупской/Парк',
);

$streets_bat = array(
    'Половинко' => 'Половинко',
    'Ушинского' => 'Ушинского',
    'Книжный' => 'Книжный',
    'Луначарского' => 'Луначарского',
    'Куйбышева' => 'Куйбышева',
    'Стадионный' => 'Стадионный',
    'Энгельса' => 'Энгельса',
    'Северная Звезда' => 'Северная Звезда',
    'Крупской' => 'Крупской',
    'Железнодорожный тупик' => 'Железнодорожный тупик',
    'Ростовский' => 'Ростовский',
    'Октябрьская' => 'Октябрьская',
    'Огородная' => 'Огородная',
    'Северный массив' => 'Северный массив',
    'Кирова' => 'Кирова',
    'Комсомольская' => 'Комсомольская',
    'Ворошилова' => 'Ворошилова',
    'Огородная' => 'Огородная',
    'Урицкого' => 'Урицкого',
    'Парковый' => 'Парковый',
    'Крупской' => 'Крупской',
    'Коваливского' => 'Коваливского',
);

//Fix this: [Левый берег]

$places_aks = array(
    'Аксай' => 'Аксай',
    'Аксай*' => 'Военный городок',
    'Аксай**' => 'Стекольный завод',
    'Аксай***' => 'Водники',
    'Аксай****' => 'Поле чудес №2',
);

$places_rnd = array(
    'Автосборочный' => 'Автосборочный',
    'Александровка' => 'Александровка',
    'Александровка*' => 'ВЖМ',
    'Аэропорт' => 'Аэропорт',
    'Аэропорт*' => 'Берберовка, Аэропорт',
    'Болгарстрой' => 'Болгарстрой',
    'Болгарстрой*' => 'Лесополоса, Болгарстрой',
    'Ботанический сад' => 'Ботанический сад (ЖДР)',
    //'Вертолетное поле' => '',
    'Военвед' => 'Военвед',
    //'ГПЗ-10' => '',
    //'Дворец спорта' => '',
    'Железнодорожный' => 'ЖДР',
    'Железнодорожный*' => 'Доватора (ЖДР, ЗЖМ)',
    //'' => 'Зеленый остров',
    'ЗЖМ' => 'ЗЖМ (Западный)',
    'ЗЖМ*' => 'Красный сад',
    'ЗЖМ**' => 'Западная промзона (ЗЖМ)',
    'ЗЖМ***' => 'Красный Маяк (ЗЖМ)',
    'ЗЖМ****' => 'Каратаево',
    'ЗЖМ*****' => 'Кумженская роща',
    'Зоопарк' => 'Зоопарк',
    'Каменка' => 'Каменка',
    'Комсомольская пл.' => 'Комсомольская площадь',
    'Левенцовский' => 'Левенцовка (ЗЖМ)',
    'Левый берег' => 'Левый берег',
    'Левый берег' => 'Заречная промзона, Левый берег',
    //'Лендворец' => '',
    'Ленина пл.' => 'Ленина',
    'Ленина пл.*' => 'площадь Ленина',
    'Мясникован' => 'Мясниковань, СЖМ',
    'Нариманова' => 'Нариманова',
    'Нахичевань' => 'Нахичевань',
    'Нахичевань*' => 'Старый автовокзал, Нахичевань',
    'Нахичевань**' => 'Красный Аксай, Нахичевань',
    'Новое поселение' => 'Новое поселение',
    'Орджоникидзе 1-й пос.' => '1 Орджоникидзе',
    'Орджоникидзе 2-й пос.' => '2 Орджоникидзе',
    'Портовая' => 'Портовая (ЖДР, ЗЖМ)',
    'Рабочий городок' => 'Рабочий городок',
    'РИИЖТ' => 'РИИЖТ',
    'Ростовское море' => 'Ростовское море',
    'Сельмаш' => 'Сельмаш',
    'СЖМ' => 'СЖМ',
    'СЖМ*' => 'СЖМ (Северный)',
    'СЖМ**' => 'Мясниковань, СЖМ',
    'СЖМ***' => 'совхоз СКВО, СЖМ',
    'Легеартис' => 'Леге-Артис, СЖМ',
    'Стройгородок' => 'Стройгородок',
    'Темерник' => 'Темерник',
    'Темерник*' => 'Темерницкий',
    'Фрунзе пос.' => 'Фрунзе',
    //'ЦГБ' => '',
    'Центр' => 'Центр',
    'Чкаловский' => 'Чкаловский',
    'Чкаловский*' => 'Мирный, Чкаловский',
    'Левый берег' => 'Левый берег',
    '1-й Пламенный' => '1 Пламенный',
    'Ашан, Леге-Артис, СЖМ' => 'Ашан, Леге-Артис, СЖМ',
    'Суворовский' => 'Суворовский',
    'Заречная промзона, Левый берег' => 'Левый берег',
);

/*
 * Парсим файл bn bncat.xml
 */

$bncat = '/home/xml/temp/bncat.xml';
//$bncat = './bncat.xml';

echo "Get and parse curent ($bncat) file; ";
echo "date: [" . date("d.m.Y H:i:s.", fileatime($bncat)) . "]; ";
echo "size: [" . size($bncat) . "]\n";

if (file_exists($bncat)) {
    $bncat_xml = @simplexml_load_file($bncat);
    echo "Ok.\n";
} else {
    echo "\nWARNING. Can't loading curent ($sheduler)\n";
    //exit(1);
}

/*
 //Создаем структуру новго xml файла

 $sxml = new SimpleXMLElement('<?xml version="1.0" encoding="utf-8"?><flats_for_sale/>');
 //$sxml->addAttribute('version', '1.3');
 //$tmp_string = '<flats_for_sale></flats_for_sale>';
 //sxml_append1($sxml, $tmp_string);

 $tmp_string = '<offer></offer>';
 sxml_append1($sxml, $tmp_string);
 
 $user_id = '7712916';
 $tmp_string = '<user-id>'.$user_id.'</user-id>';
 sxml_append1($sxml->offer[0], $tmp_string);
*/

//Создаем структуру новго xml файла
//*
$sxml = new SimpleXMLElement('<?xml version="1.0" encoding="utf-8"?><flats_for_sale/>');
//$sxml->addAttribute('version', '1.3');
$tmp_string = '<offer></offer>';
sxml_append1($sxml, $tmp_string);

//$tmp_string = '<match></match>';
//sxml_append1($sxml->offer[0], $tmp_string);

/*
$user_id = '7712916';
$tmp_string = '<user-id>'.$user_id.'</user-id>';
//sxml_append1($sxml->offer[0]->match[0], $tmp_string);
sxml_append1($sxml->offer[0], $tmp_string);
//*/

if (@is_object($bncat_xml)) {
    $count = $bncat_xml->count();
    $j = 0;
    $k = 0;
    $l = 0;
    $m = 0;
    $a = 0;

    for ($i = 0; $i < $count; $i++) {
        //for ( $i=0; $i<1100; $i++) {
        $lot_number = '';
        $place_city = '';

        $id_string = $bncat_xml->{'bn-object'}[$i]->id;
        $type = $bncat_xml->{'bn-object'}[$i]->type;
        $action = $bncat_xml->{'bn-object'}[$i]->action;
        $lot_number = substr((string)$id_string, 4, 5) . iconv('Windows-1251', 'UTF-8', chr(substr((string)$id_string, 9, 3)));
        //$new_building = trim((string)$bncat_xml->{'bn-object'}[$i]->{'new-building'};

        //$date_update = get_object_vars($bncat_xml->{'bn-object'}[$i]->date);
        //$date_update = $date_update['update'];
        //2015-02-19T22:14:29+04:00


        // >= '2015-08-14T23:59:59+03:00'

        //$lot_array
        //$date_array
        $key = '';
        $key = array_search($lot_number, $lot_array); // $key = 2;

        //FULL LOG
        if ($key != '') {
            //echo 'Exist: '.$lot_number."\n";
        } else {
            //echo 'Not Found: '.$lot_number."\n";
        }

        $update_date = $date_array[$key];

        $upDate = date('Y-m-d', strtotime($update_date));
        $upDate = new DateTime($upDate);

        $checkDate = date('Y-m-d', strtotime("-180 days"));
        $checkDate = new DateTime($checkDate);

        /*
        $date = new DateTime();
        $date->modify('+1 week');
        print $date->format('Y-m-d H:i:s');
        //OR
        print date('Y-m-d H:i:s', mktime(date("H"), date("i"), date("s"), date("m"), date("d") + 7, date("Y"));
        */

        /*
        fwrite($tmp_log, '/'.$lot_number.'/');
        fwrite($tmp_log, '*'.$key.'*');
        fwrite($tmp_log, '"'.$update_date.'"');
        fwrite($tmp_log, '('.$newDate.')');
        fwrite($tmp_log, '['.$check_date->format("U").']' . "\n");
        //fwrite($tmp_log, "------------------------------\n");
        //sleep(1);
        //*/

        if ($key != '' && $upDate->format("U") >= $checkDate->format("U")) {
            $files_image = $bncat_xml->{'bn-object'}[$i]->files->image;
            //$files_image = "no";
            if ($id_string != "") {
                //echo "$id_string\n";
                //$lot_number = substr( (string)$id_string, 4, 5) . iconv ('Windows-1251', 'UTF-8', chr (substr( (string)$id_string, 9, 3)));
                $id_new = '1508' . substr((string)$id_string, 4, 8);
                //echo "$lot_number\n";
                /*
                if ( $id_new == '140358465237') {
                 echo "$lot_number\n";
                }*/
            } else {
                echo "ERROR getting id from bncat.xml ...\n";
            }

            if ($action == 'продажа') {
                if ($type == 'квартира' && isset($id_string) && isset($files_image)) {
                    $block = TRUE;
                    //if ( $type == 'квартира' && isset($id_string) ) {
                    //Init values
                    $building_year = "";
                    //Get values
                    $is_new = $bncat_xml->{'bn-object'}[$i]->{'new-building'};
                    $date_update = $bncat_xml->{'bn-object'}[$i]->date->update;
                    //$date_update = $bncat_xml->{'bn-object'}[$i]->date->create;
                    $rooms_total = $bncat_xml->{'bn-object'}[$i]->{'rooms-total'};
                    $location_city = $bncat_xml->{'bn-object'}[$i]->location->city;
                    $location_district = $bncat_xml->{'bn-object'}[$i]->location->district;
                    $location_street = $bncat_xml->{'bn-object'}[$i]->location->street;
                    $total_value = $bncat_xml->{'bn-object'}[$i]->total->value;
                    $living_value = $bncat_xml->{'bn-object'}[$i]->living->value;
                    $kitchen_value = $bncat_xml->{'bn-object'}[$i]->kitchen->value;
                    $floor = $bncat_xml->{'bn-object'}[$i]->floor;
                    $floors = $bncat_xml->{'bn-object'}[$i]->floors;
                    $building_type = $bncat_xml->{'bn-object'}[$i]->building->type;
                    $building_year = $bncat_xml->{'bn-object'}[$i]->building->year;
                    $price_value = $bncat_xml->{'bn-object'}[$i]->price->value;
                    $agent_name = $bncat_xml->{'bn-object'}[$i]->agent->name;
                    $agent_phone = $bncat_xml->{'bn-object'}[$i]->agent->phone;
                    $url = $bncat_xml->{'bn-object'}[$i]->url;
                    $location_place = trim((string)$bncat_xml->{'bn-object'}[$i]->location->place);
                    $description_full = $bncat_xml->{'bn-object'}[$i]->description->full;
                    /*
                    $description_print = $bncat_xml->{'bn-object'}[$i]->description->{'print'};
                    $description_print = str_replace('комнатная', 'комнатная квартира', $description_print);
                    $description_print = str_replace('-комн.', 'комнатная квартира', $description_print);
                    */
                    $files_image = (array)$bncat_xml->{'bn-object'}[$i]->files;

                    $place_text = array_search($location_place, $places_bat);
                    $place_text = str_replace('*', '', $place_text);
                    $place_city = '';

                    if ($place_text != "") {
                        $place_city = 'Батайск';
                    }

                    $place_text = array_search($location_street, $streets_bat);
                    $place_text = str_replace('*', '', $place_text);

                    if ($place_text != "") {
                        $place_city = 'Батайск';
                    }

                    $place_text = array_search($location_place, $places_aks);
                    $place_text = str_replace('*', '', $place_text);

                    if ($place_text != "" && $place_city == '') {
                        $place_city = 'Аксай';
                    }

                    $place_text = array_search($location_place, $places_rnd);
                    $place_text = str_replace('*', '', $place_text);

                    if ($place_text != "" && $place_city == '') {
                        $place_city = 'Ростов-на-Дону';
                    }

                    //Check to block
                    //*
                    $block = TRUE;
                    $block_array = array(
                        'ена 1',
                        'ена 2',
                        'ена: 1',
                        'ена: 2',
                        'найти',
                        'Продажа квартир',
                        'омощь',
                        'оможем',
                        'омогу',
                        'выбрать квартиру',
                        'выбор квартир',
                        'квартир мало',
                        'родажа',
                        'квартир ',
                        'варианты',
                        '1-комнатные',
                        '2х-комнатные',
                        '1-2-3 комнатные',
                        '1-2 комнатные',
                        'Есть варианты по этажам',
                        'квартиры на других этажах',
                        'выбор квартир',
                        'торговые площади',
                    );
                    $block = strposa($description_full, $block_array);
                    if ($block == TRUE) {
                        $place_city = '';
                        echo 'Block this: [' . $description_full . ']' . "\n";
                    }
                    //*/

                    if ($place_city == '') {
                        if ($location_place != '' && $block != TRUE) {
                            echo 'Fix this: [' . $location_place . "]\n";
                        }
                    } else {

                        //  ;Квартиры;43
                        //  /real-estate/apartments-sale/new;Новостройки;44
                        //  /real-estate/apartments-sale/secondary;Вторичный рынок;45

                        /*
                        if ( $is_new == '1') {
                         $tmp_string = '<store-ad
                         validfrom="'.date("Y-m-d\TH:i:s", time()).'"
                         validtill="'.date("Y-m-d\T23:59:59", (time()+2*60*60*24)).'"
                         source-id="'.$id_new.'"
                         file-id="'.($j+1).'"
                         power-ad="1"
                         category="/real-estate/apartments-sale/new"></store-ad>';
                         sxml_append1($sxml->offer[0], $tmp_string);
                        } else {
                         $tmp_string = '<store-ad
                         validfrom="'.date("Y-m-d\TH:i:s", time()).'"
                         validtill="'.date("Y-m-d\T23:59:59", (time()+2*60*60*24)).'"
                         source-id="'.$id_new.'"
                         file-id="'.($j+1).'"
                         power-ad="1"
                         category="/real-estate/apartments-sale/secondary"></store-ad>';
                         sxml_append1($sxml->offer[0], $tmp_string);
                        }
                        //*/

                        /*
                        $tmp_string = '<is_new>'.$is_new.'</is_new>';
                        sxml_append1($sxml->offer[0]->{'store-ad'}[$j], $tmp_string);
                        */

                        $offices = array(
                            1 => 'ДОНМТ офис Центральный 1',
                            2 => 'ДОНМТ офис Центральный 2',
                            3 => 'ДОНМТ офис Центральный 3',
                            4 => 'ДОНМТ офис Западный',
                            5 => 'ДОНМТ офис Северный', //1
                            6 => 'ДОНМТ офис Северный', //2
                            7 => 'ДОНМТ офис Стройгородок',
                            8 => 'ДОНМТ офис Восточный',
                            9 => 'ДОНМТ офис Батайск',
                        );

                        $phones = array(
                            1 => '8(863)2-270-500',
                            2 => '8(863)2-990-707',
                            3 => '8(863)2-270-909',
                            4 => '8(863)200-67-67',
                            5 => '8(863)2-300-909',
                            6 => '8(863)2-500-400',
                            7 => '8(863)200-85-85',
                            8 => '8(863)300-24-00',
                            9 => '8(863)2-417-423',
                        );

                        $phones_cian = array(
                            1 => '9381361278',
                            2 => '9604434798',
                            3 => '9286216057',
                            4 => '9298174480',
                            5 => '9885669794',
                            6 => '9885669794',
                            7 => '9034067095',
                            8 => '9045033362',
                            9 => '9281879795',
                        );
                        //4=> '9282790183',

                        $key = array_search($agent_phone, $phones);
                        $agent_phone = @$phones_cian[$key];

                        //*
                        $tmp_string = '<offer></offer>';
                        sxml_append1($sxml, $tmp_string);

                        $tmp_string = '<id>' . $id_new . '</id>';
                        sxml_append1($sxml->offer[$j], $tmp_string);
                        /*
                        $tmp_string = '<date>'.$update_date.'</date>';
                        sxml_append1($sxml->offer[$j], $tmp_string);
                        //*/
                        $tmp_string = '<rooms_num>' . $rooms_total . '</rooms_num>';
                        sxml_append1($sxml->offer[$j], $tmp_string);

                        $tmp_string = '<area living="' . $living_value . '" kitchen="' . $kitchen_value . '" total="' . $total_value . '"></area>';
                        sxml_append1($sxml->offer[$j], $tmp_string);

                        $price_fix_office = iconv('Windows-1251', 'UTF-8', chr(substr((string)$id_string, 9, 3)));

                        if ($price_fix_office != '*') {
                            if (($price_value * 0.025) < 100000) {
                                $price_value = $price_value - $price_value * 0.025;
                            } else {
                                $price_value = $price_value - 90123;
                            }
                        }

                        $tmp_string = '<price currency="RUB">' . $price_value . '</price>';
                        sxml_append1($sxml->offer[$j], $tmp_string);

                        $tmp_string = '<floor total="' . $floors . '">' . $floor . '</floor>';
                        sxml_append1($sxml->offer[$j], $tmp_string);

                        $tmp_string = '<phone>' . $agent_phone . '</phone>';
                        sxml_append1($sxml->offer[$j], $tmp_string);

                        $tmp_string = '<address admin_area="39" locality="' . $place_city . '" street="' . $location_street . '" />';
                        sxml_append1($sxml->offer[$j], $tmp_string);

                        //https://regex101.com/r/oX3hL1
                        //$re = "/.дача\\s([1234])-([\\d]{4})./";
                        $re = "/.дача.*([\\d]{4})./";
                        $str = $description_full;
                        $matches = array();
                        preg_match($re, $str, $matches);
                        if (isset($matches[1])) {
                            $tmp_string = '<options object_type="2" ipoteka="1"/>';
                            sxml_append1($sxml->offer[$j], $tmp_string);
                        } else {
                            $tmp_string = '<options object_type="1"/>';
                            sxml_append1($sxml->offer[$j], $tmp_string);
                        }

                        $tmp_string = '<note>' . "\n" . '<![CDATA[' . $description_full . "\n" .
                            '  При звонке в ' . $offices[$key] . ' укажите лот: ' .
                            substr((string)$id_string, 4, 5) . '-8' .
                            iconv('Windows-1251', 'UTF-8', chr(substr((string)$id_string, 9, 3))) .
                            //"\n" . $location_place . "\n" .
                            ']]>' . "\n" .
                            '</note>';

                        sxml_append1($sxml->offer[$j], $tmp_string);

                        //$tmp_string = '<publish cian="yes" rentlist="yes"></publish>';
                        //$tmp_string = '<publish cian="yes"></publish>';
                        //sxml_append1($sxml->offer[$j], $tmp_string);

                        //<photo>http://www.website.ru/images/image1.jpg</photo>
                        if (@is_array($files_image['image'])) {
                            //$tmp_string = '<fotos></fotos>';
                            //sxml_append1($sxml->offer[$j], $tmp_string);
                            foreach ($files_image['image'] as $image) {
                                $tmp_string = '<photo>' . $image . '</photo>';
                                sxml_append1($sxml->offer[$j], $tmp_string);
                                //sxml_append1($sxml->offer[$j]->fotos[0], $tmp_string);
                            }
                        } else {
                            //$tmp_string = '<fotos></fotos>';
                            //sxml_append1($sxml->offer[$j], $tmp_string);
                            $tmp_string = '<photo>' . $files_image . '</photo>';
                            sxml_append1($sxml->offer[$j], $tmp_string);
                            //sxml_append1($sxml->offer[$j]->fotos[0], $tmp_string);
                        }
                        echo '.';
                        $j++;
                    }
                } elseif ($type == 'комната') {
                    $k++;
                } elseif ($type == 'дом' && isset($id_string) && isset($files_image)) {
                    //*****************************************************************/
                    //Init values
                    $building_year = "";
                    //Get values
                    //$is_new = $bncat_xml->{'bn-object'}[$i]->{'new-building'};
                    $date_update = $bncat_xml->{'bn-object'}[$i]->date->update;
                    //$date_update = $bncat_xml->{'bn-object'}[$i]->date->create;
                    $rooms_total = $bncat_xml->{'bn-object'}[$i]->{'rooms-total'};
                    $building_year = $bncat_xml->{'bn-object'}[$i]->building->year;
                    $floors = $bncat_xml->{'bn-object'}[$i]->floors;
                    $total_value = $bncat_xml->{'bn-object'}[$i]->total->value;
                    $living_value = $bncat_xml->{'bn-object'}[$i]->living->value;
                    $kitchen_value = $bncat_xml->{'bn-object'}[$i]->kitchen->value;
                    $lot_value = $bncat_xml->{'bn-object'}[$i]->lot->value;
                    $price_value = $bncat_xml->{'bn-object'}[$i]->price->value;
                    $location_country = $bncat_xml->{'bn-object'}[$i]->location->country;
                    $location_region = $bncat_xml->{'bn-object'}[$i]->location->region;
                    $location_city = $bncat_xml->{'bn-object'}[$i]->location->city;
                    $location_district = $bncat_xml->{'bn-object'}[$i]->location->district;
                    $location_place = $bncat_xml->{'bn-object'}[$i]->location->place;
                    $location_street = $bncat_xml->{'bn-object'}[$i]->location->street;

                    $description_full = $bncat_xml->{'bn-object'}[$i]->description->full;
                    $description_print = $bncat_xml->{'bn-object'}[$i]->description->{'print'};

                    $files_image = (array)$bncat_xml->{'bn-object'}[$i]->files;

                    $agent_name = $bncat_xml->{'bn-object'}[$i]->agent->name;
                    $agent_phone = $bncat_xml->{'bn-object'}[$i]->agent->phone;
                    $url = $bncat_xml->{'bn-object'}[$i]->url;

                    $place_text = array_search($location_place, $places_bat);
                    $place_text = str_replace('*', '', $place_text);

                    if ($place_text != "") {
                        $place_city = 'Батайск';
                    }

                    $place_text = array_search($location_place, $places_aks);
                    $place_text = str_replace('*', '', $place_text);

                    if ($place_text != "") {
                        $place_city = 'Аксай';
                    }

                    $place_text = array_search($location_place, $places_rnd);
                    $place_text = str_replace('*', '', $place_text);
                    if ($place_text != "") {
                        $place_city = 'Ростов-на-Дону';
                    }

                    if ($place_city == '') {
                        if ($location_place != '') {
                            echo 'Fix this: [' . $location_place . "]\n";
                        }
                    } else {

                        $j++;
                        //*****************************************************************/
                    }
                    $l++;
                } elseif ($type == 'участок') {

                    $m++;
                }
            } elseif ($action == 'аренда') {
                $a++;
            }
        }
    }
    echo "[$count] records total. \n";
    echo "kv[$j] kom[$k] dom[$l] uch[$m] ar[$a] records in file. \n";
} else {
    echo "\nWARNING. Can't loading  ($bn_cat)\n";
}

$dom = new DOMDocument('1.0');
$dom->preserveWhiteSpace = false;
$dom->formatOutput = true;
$irr_asxml = $sxml->asXML();
$dom->loadXML($irr_asxml);

$new_irr = '/home/xml/export/cian/cian.xml';
//$new_irr= './cian.xml';

$dom->save($new_irr);
echo "Ok. ";
echo "date: [" . date("d.m.Y H:i:s.", fileatime($new_irr)) . "]; ";
echo "size: [" . size($new_irr) . "]\n";

unset ($irr_asxml);
unset ($bncat_xml);

echo "Create GZip...";
//Create GZip
// Name of the file we are compressing
$file = $new_irr;

// Name of the gz file we are creating
$gzfile = '/home/xml/export/cian/cian.xml.gz';
//$gzfile = './cian.xml.gz';

// Open the gz file (w9 is the highest compression)
$fp = gzopen($gzfile, 'w9');

// Compress the file
gzwrite($fp, file_get_contents($file));

// Close the gz file and we are done
gzclose($fp);
echo "Ok.\n";

$uid = 'xml';
$gid = 'xml';

echo "Fix permissions...";
chown($gzfile, $uid);
chgrp($gzfile, $gid);
echo "Ok.\n";

//*
//fwrite($tmp_log, "------------------------------\n");
//fwrite($tmp_log, "------------------------------\n");
//fclose($tmp_log);
//*/

$time = round(microtime(true) - $start, 3);
echo "+-------------------------------------------------------------+\n";
echo "|                  All done by $time seconds                ||\n";
echo "+-------------------------------------------------------------+\n";
?>
