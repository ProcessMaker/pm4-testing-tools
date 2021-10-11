<?php

use Illuminate\Support\Facades\Artisan;

Artisan::command('hello {name?}', function () {
    $name = $this->argument('name') ?? 'World';
    $this->comment("Hello {$name}");
})->describe('Display a hello world message');
