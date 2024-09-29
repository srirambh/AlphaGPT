import { Input } from "@/components/ui/input";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { postModel } from "./requests";
import { useForm } from "react-hook-form";
import { Label } from "@/components/ui/label";
import { IoIosSend } from "react-icons/io";

export default function Home() {
  const queryClient = useQueryClient();
  const { register, handleSubmit } = useForm();
  const { mutate } = useMutation({
    mutationFn: postModel,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["models"] });
      console.log("postModel success!");
    },
  });
  async function onSubmit(data: any) {
    mutate(data);
  }
  return (
    <main className="w-full flex flex-col items-center justify-around">
      <h1 className="text-foreground text-3xl font-bold">AlphaGPT</h1>
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="w-[768px] flex flex-col items-center space-y-6"
      >
        <Label htmlFor="prompt" className="text-2xl">
          Let's build your refined LLM.
        </Label>
        <div className="w-full flex flex-row items-center space-x-4 rounded-full border-2 border-border p-2">
          <Input
            {...register("prompt")}
            id="prompt"
            className="w-full text-2xl rounded-none font-light py-6 px-5 border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
            type="text"
            placeholder="Ask AlphaGPT for a customized LLM"
          />
          <button
            type="submit"
            className="min-w-[56px] h-[56px] rounded-full bg-blue-200 border-2 flex flex-col items-center justify-center hover:cursor-pointer hover:scale-110 transition-transform active:scale-90"
          >
            <IoIosSend className="w-[32px] h-[32px]" />
          </button>
        </div>
      </form>
    </main>
  );
}
