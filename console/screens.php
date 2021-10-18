<?php

use Illuminate\Support\Facades\Artisan;
use ProcessMaker\Jobs\ImportScreen;

Artisan::command('test:screen', function () {
    $options = [];
    foreach (glob(__DIR__ . '/screens/*.json') as $screen) {
        $options[] = basename($screen, '.json');
    }
    $name = $this->choice('Available screens:', $options);
    $file = __DIR__ . '/screens/' . $name . '.json';
    $content = file_get_contents($file);
    ImportScreen::dispatchNow($content);
})->describe('Import a testing screen');
