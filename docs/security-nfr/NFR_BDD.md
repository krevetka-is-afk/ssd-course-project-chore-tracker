# NFR_BDD.md — в формате Gherkin

Feature: Security & performance NFR acceptance Chore Tracker

  @NFR-Auth-Hash
  Scenario: Пароли хранятся только в Argon2id конфигурации
    Given репозиторий с кодом сервиса и secrets настроены на stage
    When выполняется unit/integration тест "auth:hash-config"
    Then конфиг хэширования должен быть Argon2id с параметрами t>=3, m>=256MB, p>=1

  @NFR-JWT
  Scenario: TTL access token и refresh token соблюдены
    Given пользователь получает access и refresh токены на stage
    When пользователь получает новые токены через логин
    Then access token TTL ≤ 15 минут и refresh token TTL ≤ 7 дней

  @NFR-OwnerOnly
  Scenario: Owner-only authorization для модификации Assignment
    Given Существует Assignment A, принадлежащий user U1, и существует user U2 (не владелец)
    When U2 делает PUT /assignments/{A.id} с валидными данными
    Then Ответ должен быть 403 Forbidden и Assignment не изменён

  @NFR-Perf-Stats
  Scenario: p95 GET /stats не превышает 200 ms при 20 RPS
    Given stage окружение с production-like конфигурацией и нагрузкой 20 RPS
    When запускается 5-минутный нагрузочный тест на GET /stats
    Then p95 времени ответа ≤ 200 ms

  @NFR-Vuln-SLA-negative
  Scenario: Если Critical vulnerability не исправлена в SLA, сборка помечается как failed
    Given CI получает SCA-отчёт с критической уязвимостью в dependency
    When прошло 8 дней со времени обнаружения уязвимости и MR с фиксами отсутствует
    Then CI помечает задачу как blocked/fail и создаётся Issue с приоритетом High
