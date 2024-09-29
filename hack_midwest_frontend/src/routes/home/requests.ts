import axios from "axios";

const sleep = (delay: number) =>
  new Promise((resolve) => setTimeout(resolve, delay));

export async function postModel(formData: any) {
  console.log("postModel called! payload:", formData);
  // return axios.post(`${import.meta.env.VITE_BASE_ENDPOINT}`, formData);
  // TODO: PLACEHOLDER
  return sleep(750);
}
