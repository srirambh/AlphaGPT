import axios from "axios";

const sleep = (delay: number) =>
  new Promise((resolve) => {
    setTimeout(resolve, delay);
  });
export async function getModels() {
  console.log("Executing getModels!");
  // return axios.get(`${import.meta.env.VITE_BASE_ENDPOINT}`);
  // TODO: PLACEHOLDER
  return sleep(750);
}
