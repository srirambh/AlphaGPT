import axios from "axios";

export async function postFile(data) {
  console.log("executing postFile", data);
  // const formData = new FormData();
  // if (data.file.length != 0 | !data.file[0]) {
  //   formData.append("file", data.file[0]);
  // }

  return axios.post(
    `${import.meta.env.VITE_BASE_ENDPOINT}filePost/${data.projectid}/${data.workerid}`,
    data,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );
}
