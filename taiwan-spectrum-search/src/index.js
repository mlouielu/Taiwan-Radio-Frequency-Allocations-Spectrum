import React from 'react';
import ReactDOM from 'react-dom';

import Container from '@material-ui/core/Container';
import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import Link from '@material-ui/core/Link';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import WifiIcon from '@material-ui/icons/Wifi';
import CommentIcon from '@material-ui/icons/Comment';

import spectrum from './data/spectrum.json';


function checkFreqRange(freq) {
  freq = parseFloat(freq);

  var allocations = []
  spectrum['spectrum'].forEach(e => {
	if (e['range'][0] <= freq && freq <= e['range'][1]) {
	  allocations.push(e);
	}
  });

  return allocations;
}

var style = {
    backgroundColor: "#F8F8F8",
    borderTop: "1px solid #E7E7E7",
    textAlign: "center",
    position: "fixed",
    left: "0",
    bottom: "0",
    height: "100px",
    width: "100%",
    padding: "10px 0 0 0",
}

var phantom = {
  display: 'block',
  height: '100px',
  padding: "10px 0 0 0",
  width: '100%',
}

function Footer() {
    return (
        <div>
            <div style={phantom} />
            <div style={style}>
			  <Link href="https://github.com/mlouielu/Taiwan-Radio-Frequency-Allocations-Spectrum">GitHub - Taiwan Radio Frequency Allocations Spectrum</Link>
            </div>
        </div>
    )
}

export default Footer

class TaiwanSpectrum extends React.Component {
  constructor(props) {
    super(props);

	this.state = {
	  allocations: []
	};

	this.keyPress = this.keyPress.bind(this);
	this.renderAllocation = this.renderAllocation.bind(this);
  }

  keyPress(e) {
	if (e.key === 'Enter') {
	  let freq = e.target.value;
	  let allocations = checkFreqRange(freq);
	  this.setState({allocations: allocations});

	  e.preventDefault();
	}
  }

  renderAllocation(alloc) {
    const { classes } = this.props;
	return (<Grid item xs={12} md={4}>
			  <Card>
				<CardContent>
				  <Typography color="textSecondary" style={{'fontSize': '0.6rem'}}>
				  pp. {alloc['page_number']}
				</Typography>
				<Typography variant="h5" component="h2">
				  {alloc['range'][0]} - {alloc['range'][1]} {alloc['unit']}
				</Typography>
				<List>
				  {alloc['usage'].map((usage) =>
					<ListItem style={{'fontSize': '0.8rem'}}>
					  <ListItemIcon>
						<WifiIcon />
					  </ListItemIcon>
					  {usage}
					</ListItem>)}
				</List>
				  <Typography color="textSecondary">
				<List>
				  {alloc['note'].map((note) =>
					<ListItem style={{'fontSize': '0.6rem'}}>
					  <ListItemIcon>
						<CommentIcon />
					  </ListItemIcon>
					  {note}
					</ListItem>)}
				</List>
				</Typography>

			  </CardContent>
			  </Card>
			</Grid>
		   );
  }

  renderAllocations(allocations) {
	if (allocations.length <= 0) {
	  return;
	}

	return (
	  allocations.map((alloc) => this.renderAllocation(alloc))
	);
  }

  render () {
    const { classes } = this.props;
	console.log(classes);
	return (
	  <Container>
		<Box>
		  <Typography variant='h3' component='h1'>台灣無線電頻率分配查詢</Typography>
		  <Grid container spacing={3}>
			<Grid item xs={12}>
			  <form>
				<TextField onKeyDown={this.keyPress}
						   label="輸入欲查詢頻率"
						   fullWidth="true"></TextField>
			  </form>
			</Grid>
		  </Grid>
		  <Grid container spacing={3}>
			{ this.renderAllocations(this.state.allocations) }
		  </Grid>
		</Box>
		<Footer />
	  </Container>
	);
  }
}

ReactDOM.render(
  <TaiwanSpectrum />,
  document.getElementById('root')
);
