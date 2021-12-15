<?php

use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Str;

Artisan::command('cypress:test {screen}', function () {

    // get artisan screen argument
    $screen = $this->argument('screen');
    if(!file_exists($screen)) {
        $this->error('File not found: ' . $screen);
    }
    // Check if tests/e2e/fixtures exists (means we are in screen-builder)
    if (!file_exists('./tests/e2e/fixtures')) {
        $this->error('You must be in screen-builder to run this command');
    }

    $filepath = $screen;
    $testScreenFile = basename($filepath);
    $testName = str_replace('_', ' ', Str::snake(basename($filepath, '.json'), ' '));
    $testFileName = ucfirst(Str::camel(basename($filepath, '.json'))) . '.spec.js';
    // Copy screen to tests/e2e/fixtures/ if not exists
    $fixturePath = './tests/e2e/fixtures/' . $testScreenFile;
    if (!file_exists($fixturePath)) {
        copy($filepath, $fixturePath);
    }
    // Create spec file
    $specFile = './tests/e2e/specs/' . $testFileName;
    if (!file_exists($specFile)) {
        $this->info('Creating spec file: ' . $specFile);
        $spec = file_get_contents(__DIR__ . '/cypress/test_screen.spec.js');
        $spec = str_replace('{testName}', $testName, $spec);
        $spec = str_replace('{testScreenFile}', $testScreenFile, $spec);
        file_put_contents($specFile, $spec);
    }
})->describe('Create a test from a screen file');
