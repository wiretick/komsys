<script>
	export let data;
</script>

<div class="mx-auto">
    <table class="table-auto border border-collapse text-left bg-white shadow sm:rounded-lg">
        <thead class="uppercase text-xs bg-gray-50 text-gray-700">
            <tr class="border border-collapse">
                <th class="px-6 py-3">Group</th>
                <th class="px-6 py-3">Task</th>
                <th class="px-6 py-3">Status</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {#each data.groups as { group, task, status }}
                <tr class="border border-collapse">
                    <td class="px-6 py-4 text-center">{group}</td>
                    <td class="px-6 py-4 text-center">{task}</td>
                    <td class="px-6 py-4">
                        <span class="bg-red-100 text-red-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-red-900 dark:text-red-300">{status}</span>
                    </td>
                    <td class="px-6 py-4 text-right">
                        <a href="#yup" class="font-medium text-blue-600 dark:text-blue-500 hover:underline">On my way</a>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>