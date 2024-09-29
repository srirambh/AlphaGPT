import { Link } from "react-router-dom";
import { Button } from "./components/ui/button";
import { ScrollArea } from "./components/ui/scroll-area";
import { Separator } from "./components/ui/separator";
import { useQuery } from "@tanstack/react-query";
import { getModels } from "./requests";
import { projects } from "./db/db";
import { useEffect, useState } from "react";
import { Progress } from "./components/ui/progress";

export default function Sidebar() {
  const [progress, setProgress] = useState(13);
  const { data, isPending } = useQuery({
    queryKey: ["models"],
    queryFn: getModels,
  });
  useEffect(() => {
    const timer = setTimeout(() => setProgress(77), 3000);
    return () => clearTimeout(timer);
  }, []);
  return (
    <div className="min-w-40 border-b border-border/40 bg-primary/95 backdrop-blur supports-[backdrop-filter]:bg-primary/60 z-10 flex flex-col items-center space-y-10 pt-10">
      <Button
        className="min-h-28 min-w-28 hover:scale-105 transition-transform"
        asChild
      >
        <Link to="/">
          <p className="text-primary-foreground font-bold text-5xl">+</p>
        </Link>
      </Button>
      <Separator className="w-[120px]" />
      <ScrollArea className="w-full h-full">
        <div className="flex flex-col space-y-10 items-center">
          {isPending ? (
            <Button
              className="h-[100px] w-[100px] hover:scale-105 transition-transform"
              asChild
            >
              <p className="text-primary-foreground">...</p>
            </Button>
          ) : (
            projects.map(
              //TODO: Placeholder -> change projects to data
              (project, idx: number) =>
                project.state == "ready" ? (
                  <Button
                    key={idx}
                    className="h-[100px] w-[100px] hover:scale-105 transition-transform bg-secondary hover:bg-background"
                    asChild
                  >
                    <Link to={`/${project.id}`}>
                      <p className="text-secondary-foreground">
                        {project.name}
                      </p>
                    </Link>
                  </Button>
                ) : (
                  <Button
                    key={idx}
                    className="h-[100px] w-[100px] flex flex-col items-center justify-around bg-secondary/50 hover:bg-background/50"
                    asChild
                  >
                    <Link to={`/${project.id}`}>
                      <p className="text-secondary-foreground">
                        {project.name}
                      </p>
                      <Progress value={progress} className="h-[10px] border" />
                    </Link>
                  </Button>
                ),
            )
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
