<script>
  import { onMount } from "svelte";
  import { writable } from "svelte/store";

  // const state = writable({
  //   notifications: [],
  // });

  // function get_notifications() {
  //   const ws = new WebSocket("ws://mqtt20.iik.ntnu.no:1883/mqtt");

  //   ws.addEventListener("message", (message) => {
  //     const data = JSON.parse(message.data);
  //     state.update((state) => ({
  //       ...state,
  //       notifications: [data].concat(state.notifications),
  //     }));
  //   });
  // }

  let tasks = [];
  const notifications = writable([]);

  onMount(async () => {
    const res = await fetch(`http://127.0.0.1:8000/tasks`);
    tasks = await res.json();

    // Notification stuff
    const evtSrc = new EventSource(`http://localhost:8000/notifications`);
    evtSrc.onmessage = function (event) {
      notifications.update((arr) => arr.concat(event.data));
      // console.log(event.data);
    };

    evtSrc.onerror = function (event) {
      console.log(event);
    };
  });

  function on_my_way() {
    console.log("Clicked");
  }
</script>

<div class="mx-auto">
  <table
    class="table-auto border border-collapse text-left bg-white shadow sm:rounded-lg"
  >
    <thead class="uppercase text-xs bg-gray-50 text-gray-700">
      <tr class="border border-collapse">
        <th class="px-6 py-3">Group</th>
        <th class="px-6 py-3">Task</th>
        <th class="px-6 py-3">Status</th>
        <th />
      </tr>
    </thead>
    <tbody>
      {#each tasks as { group, task, status }}
        <tr class="border border-collapse">
          <td class="px-6 py-4 text-center">{group}</td>
          <td class="px-6 py-4">#{task.id}, {task.title}</td>
          <td class="px-6 py-4">
            <span class="badge-red">{status}</span>
          </td>
          <td class="px-6 py-4 text-right">
            <a href="#yup" on:click={on_my_way} class="blue-link">On my way</a>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>

  {#each $notifications as n}{n}{/each}
</div>
