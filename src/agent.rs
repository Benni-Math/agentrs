use rustc_hash::FxHashMap;

use crate::operation::Operation;

/// First draft of agents could have a vector of properties,
/// but this will cause Vec<Agents> to essentially be Vec<Vec<i64>>
/// (or whatever numeric value we are using)
/// Look into using some sort of 'smart array'? or SmallVec?
/// The main thing is that I want the agents to be contiguous in memory
/// And I don't want the Python code to have direct access to it,
/// they can only 'build' it

// TODO: fix lifetime mess
pub struct Agent<'a> {
    pub properties: FxHashMap<&'a str, i64>,
    // Could also wrap operations as Box<AgentType> (useful when we add more info?)
    // (or maybe Rc<AgentType>, since multiple 'owners'? but not mutation)
    operations: &'a Vec<Operation<'a>>,
}

impl Agent<'_> {
    pub fn factory<'a>(
        init_prop: FxHashMap<&'a str, i64>,
        operations: Vec<Operation<'a>>,
    ) -> AgentFactory<'a> {
        AgentFactory::new(init_prop, operations)
    }

    /// Take a single time step for an agent.
    /// First draft will not implement network interactions
    /// This is not parallelized, since we are assuming parallelization on the model level
    pub fn step(self) -> Self {
        self.operations
            .iter()
            .fold(self, |agent, op| agent.apply(op))
    }

    fn apply(self, op: &Operation) -> Self {
        match op {
            Operation::AddToProperty(_) => { self }
        }
    }
}

pub struct AgentFactory<'a> {
    // Not efficient to have this be a hashmap,
    // then we are cloning it each time we build,
    // will have tons of hashmaps, instead of using contiguous memory
    // TODO: change this and the agent properties to something else
    init_prop: FxHashMap<&'a str, i64>,
    operations: Vec<Operation<'a>>,
}

impl<'a> AgentFactory<'a> {
    fn new(init_prop: FxHashMap<&'a str, i64>, operations: Vec<Operation<'a>>) -> Self {
        Self {
            init_prop,
            operations,
        }
    }

    pub fn create_agent(&self) -> Box<Agent> {
        Box::new(Agent {
            properties: self.init_prop.clone(),
            operations: &self.operations,
        })
    }
}
