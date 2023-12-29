/// First draft of agents could have a vector of properties,
/// but this will cause Vec<Agents> to essentially be Vec<Vec<i64>>
/// (or whatever numeric value we are using)
/// Look into using some sort of 'smart array'? or SmallVec?
/// The main thing is that I want the agents to be contiguous in memory
/// And I don't want the Python code to have direct access to it,
/// they can only 'build' it

trait Agent {

}

struct AgentBuilder {

}

impl AgentBuilder {
    fn new() -> Self {
        Self {}
    }

    fn build(&self) -> Agent {
        Agent {}
    }
}
