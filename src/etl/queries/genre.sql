SELECT id::uuid, name
FROM content.genre
WHERE modified > $1
ORDER BY modified