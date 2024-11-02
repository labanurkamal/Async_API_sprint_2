SELECT
pfw.person_id::uuid AS id,
p.full_name AS full_name,
fw.id::uuid as film_work_id,
fw.title as title,
fw.rating as imdb_rating,
STRING_AGG(DISTINCT pfw.role, ', ') AS roles
FROM "content".film_work AS fw
JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
JOIN content.person AS p ON p.id = pfw.person_id
WHERE p.created > $1
GROUP BY pfw.person_id, p.full_name, fw.id;

