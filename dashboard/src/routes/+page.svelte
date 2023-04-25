<script>
  import "../app.css";
  import { goto } from "$app/navigation";
  import { clientID, globalNotifications } from "./store.js";

  function chose_ta() {
    globalNotifications.set(true);
    clientID.set(0);
    goto("/dashboard");
  }

  function chose_staff() {
    globalNotifications.set(false);
    clientID.set(1);
    goto("/dashboard");
  }
</script>

<div class="grid place-content-center mt-16">
  <div>
    <h1 class="text-8xl my-16">Entry page</h1>
    <div class="text-center">
      <button
        on:click={chose_ta}
        type="button"
        class="text-purple-700 hover:text-white border border-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:border-purple-400 dark:text-purple-400 dark:hover:text-white dark:hover:bg-purple-500 dark:focus:ring-purple-900"
        >Teaching assistant</button
      >
      <button
        on:click={chose_staff}
        type="button"
        class="text-purple-700 hover:text-white border border-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:border-purple-400 dark:text-purple-400 dark:hover:text-white dark:hover:bg-purple-500 dark:focus:ring-purple-900"
        >Course staff</button
      >
    </div>
  </div>
</div>
