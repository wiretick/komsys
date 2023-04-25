import { writable } from "svelte/store";

export const globalNotifications = writable(true);
export const clientID = writable(0);
