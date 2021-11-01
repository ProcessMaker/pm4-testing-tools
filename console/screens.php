<?php

use Illuminate\Support\Facades\Artisan;
use ProcessMaker\Jobs\ImportScreen;

Artisan::command('test:screen {--t= : Input the ticket number of the screen to import}', function () {
    $options = [];
    foreach (glob(__DIR__ . '/screens/*.json') as $screen) {
        $options[] = basename($screen, '.json');
    }
    $name = ($this->option('t') ? $this->option('t') : $this->choice('Available screens', $options));
    $file = __DIR__ . '/screens/' . $name . '.json';

    if(file_exists($file)) {
        $content = file_get_contents($file);
        ImportScreen::dispatchNow($content);
    } else {
        $this->error('Screen file not found: ' . $file);
        if($this->confirm('Do you want to see the screen list?')){
            $name = $this->choice('Available screens', $options);
        }
    }

})->describe('Import a testing screen');
