import {
  Divider,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import BaseCard from "./BaseCard";

function ListCard({ title, content }) {
  return (
    <BaseCard title={title}>
      <List dense={true}>
        <Divider />
        {Object.keys(content).map((key) => {
          return (
            <>
              <ListItem secondaryAction={<>test</>}>
                <ListItemText primary={key} />
              </ListItem>
              <Divider />
            </>
          );
        })}
      </List>
    </BaseCard>
  );
}

export default ListCard;
