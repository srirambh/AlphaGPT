import axios from "axios";

const sleep = (delay: number) =>
  new Promise((resolve) => {
    setTimeout(resolve, delay);
  });
export async function getModel() {
  console.log("Executing getModels!");
  // return axios.get(`${import.meta.env.VITE_BASE_ENDPOINT}`);
  // TODO: PLACEHOLDER
  return sleep(750);
}

export async function filePost(data) {
  console.log("Executing filePost mainGPT!", data);
  // const formData = new FormData();
  // formData.append("prompt", data["prompt"]);
  // for (let i = 0; i < data.file.length; i++) {
  //   formData.append("file[]", data.file[i]);
  // }

  return axios.post(
    `${import.meta.env.VITE_BASE_ENDPOINT}filePost/${data.projectid}`,
    data,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );
}
