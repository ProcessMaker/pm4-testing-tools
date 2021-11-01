<?php

use Illuminate\Support\Facades\Artisan;
use ProcessMaker\Jobs\ImportProcess;

Artisan::command('test:process {--t= : Input the ticket number of the process to import}', function () {
    $options = [];

    foreach (glob(__DIR__ . '/processes/*.json') as $process) {
        $options[] = basename($process, '.json');
    }

    $name = ($this->option('t') ? $this->option('t') : $this->choice('Available processes', $options));
    $file = __DIR__ . '/processes/' . $name . '.json';

    if(file_exists($file)) {
        $content = file_get_contents($file);
        ImportProcess::dispatchNow($content);
    } else {
        $this->error('Process file not found: ' . $file);
        if($this->confirm('Do you want to see the processes list?')){
            $name = $this->choice('Available processes', $options);
        }
    }
})->describe('Import a testing process');
