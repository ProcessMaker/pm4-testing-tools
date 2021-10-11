<?php

use Illuminate\Support\Facades\Artisan;
use ProcessMaker\Models\User;

Artisan::command('users', function () {
    dump(User::pluck('username')->toArray());
})->describe('List all stored user names');
