// Зеркалит валидацию бэкенда (app/schemas/user.py), чтобы пользователь узнавал
// об ошибке сразу в форме, а не после round-trip на сервер и обратно (422).
export const PASSWORD_MIN_LENGTH = 8
