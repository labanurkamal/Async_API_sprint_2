SELECT
    fw.id::text AS film_work_id,
    fw.title,
    fw.description,
    STRING_AGG(DISTINCT p.id::text, ', ') AS person_ids,
    STRING_AGG(DISTINCT p.full_name || ':' || pfw.role, ', ') AS persons_with_roles,
    STRING_AGG(DISTINCT g.id::text || ':' || g.name, ', ') AS genres,
    fw.rating AS imdb_rating,
    fw.created AS creation_date
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.modified > $1
  AND ($2 IS NULL OR pfw.person_id IS NULL OR pfw.person_id = ANY($2))
GROUP BY fw.id, fw.title, fw.description, fw.rating, fw.created;
