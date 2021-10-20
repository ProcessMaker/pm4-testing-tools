## Install
```
composer global require processmaker/pm4-testing-tools
```

## Use
```
> pm4tools hello World
  Hello World
```

## Develop
### Add console commands
Create a php artisan command inside `console` folder
e.g.
```
<?php

use Illuminate\Support\Facades\Artisan;
use ProcessMaker\Models\User;

Artisan::command('users', function () {
    dump(User::pluck('username')->toArray());
})->describe('List all stored user names');

```

### Import testing screen
```
> pm4tools test:screen
 Available screens::
  [0] validation rules loop
 > 0
```

### Create n users
To create 3 non admin users:
```
> pm4tools create:user 3
```
