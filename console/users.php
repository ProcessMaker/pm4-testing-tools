<?php

use Illuminate\Support\Facades\Artisan;
use ProcessMaker\Models\User;

Artisan::command('users', function () {
    dump(User::pluck('username')->toArray());
})->describe('List all stored user names');

Artisan::command('create:user {count?}', function () {
    $count = intval($this->argument('count') ?? 1);
    factory(User::class, $count)->create([
        'status' => 'ACTIVE',
    ]);
})->describe('List all stored user names');
