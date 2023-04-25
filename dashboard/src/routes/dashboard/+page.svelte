<script>
  /** @type {import('./$types').PageData} */
  export let data;

  import { onMount } from "svelte";
  import { invalidateAll } from "$app/navigation";
  import { globalNotifications } from "../store.js";
  import { clientID } from "../store.js";

  const Status = {
    WAITING: "Waiting",
    GETTING_HELP: "Getting help",
    WORKING: "Working",
  };

  let enabledNotifications = true;
  let globalNotificationsValue;


  globalNotifications.subscribe((value) => {
    globalNotificationsValue = value;
  });

  let clientIDValue;
  clientID.subscribe((value) => {
    clientIDValue = value;
  });

  onMount(async () => {
    Notification.requestPermission().then();

    const evtSrc = new EventSource(`http://localhost:8000/notifications?client_id=${clientIDValue}`);

    evtSrc.onmessage = function (event) {
      // if (globalNotificationsValue && enabledNotifications && event.data) {
        if (event.data) {
        new Notification(event.data);
      }

      invalidateAll();
    };
  });

  async function on_my_way(group) {
    await fetch(`http://localhost:8000/help_is_coming/${group}?client_id=${clientIDValue}`, {
      method: "POST",
    });

    enabledNotifications = false;

    invalidateAll();
  }

  async function finished(group) {
    await fetch(`http://localhost:8000/help/${group}`, {
      method: "DELETE",
    });

    enabledNotifications = true;

    invalidateAll();
  }

  function get_color(status) {
    switch (status) {
      case Status.WAITING:
        return "badge-red";
      case Status.GETTING_HELP:
        return "badge-yellow";
      default:
        return "badge-green";
    }
  }
</script>

<div class="mx-auto">
  <h1 class="text-xl mb-3">Help queue</h1>
  <table
    class="table-auto border border-collapse text-left bg-white shadow sm:rounded-lg mb-6"
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
      {#each data.queue as { group, task, status }}
        <tr class="border border-collapse">
          <td class="px-6 py-4 text-center">{group}</td>
          <td class="px-6 py-4">#{task}</td>
          <td class="px-6 py-4">
            <span class={get_color(status)}>{status}</span>
          </td>

          {#if Status.WAITING == status}
            <td class="px-6 py-4 text-right">
              <a href="#omw" on:click={() => on_my_way(group)} class="blue-link"
                >On my way</a
              >
            </td>
          {:else if Status.GETTING_HELP == status}
            <td class="px-6 py-4 text-right">
              <a href="#fin" on:click={() => finished(group)} class="blue-link"
                >Finished</a
              >
            </td>
          {/if}
        </tr>
      {/each}
    </tbody>
  </table>

  <h1 class="text-xl mb-3">Groups status</h1>
  <table
    class="table-auto border border-collapse text-left bg-white shadow sm:rounded-lg"
  >
    <thead class="uppercase text-xs bg-gray-50 text-gray-700">
      <tr class="border border-collapse">
        <th class="px-6 py-3">Group</th>
        <th class="px-6 py-3">Task</th>
        <th class="px-6 py-3">Status</th>
      </tr>
    </thead>
    <tbody>
      {#each data.groups as { group, task, status }}
        <tr class="border border-collapse">
          <td class="px-6 py-4 text-center">{group}</td>
          <td class="px-6 py-4">#{task}</td>
          <td class="px-6 py-4">
            <span class={get_color(status)}>{status}</span>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
