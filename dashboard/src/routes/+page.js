/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params }) {
  const queue_res = await fetch(`http://127.0.0.1:8000/queue`);
  const groups_res = await fetch(`http://127.0.0.1:8000/tasks`);

  return {
    queue: await queue_res.json(),
    groups: await groups_res.json(),
  };
}
