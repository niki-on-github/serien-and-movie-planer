import {
  Card,
  CardContent,
  CardHeader,
  Divider,
} from "@mui/material";

const BaseCard = ({ title, divider=false, children }) => {
  return (
    <Card sx={{ borderRadius: 3 }}>
      {title && <CardHeader title={title} />}
      {divider && <Divider />}
      <CardContent>{children}</CardContent>
    </Card>
  );
}

export default BaseCard;
